from decimal import Decimal
import uuid
from urllib.parse import urlencode
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model, login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings
from base.models import BaseProduct, Cart, CartItem, Order, OrderItem, Address
from ERP.models import Category, StoreStat

User = get_user_model()

CART_SESSION_KEY = 'cart'
PLACEHOLDER_IMAGE = 'https://via.placeholder.com/300x300'


def _get_product_images(product):
    carousel_images = []
    if getattr(product, 'image', None):
        try:
            url = product.image.url
            carousel_images.append(url)
        except Exception:
            pass
    for extra in getattr(product, 'extra_images', []).all() if hasattr(product, 'extra_images') else []:
        try:
            url = extra.image.url
            carousel_images.append(url)
        except Exception:
            pass
    if not carousel_images:
        carousel_images.append(PLACEHOLDER_IMAGE)
    return carousel_images


def _get_session_cart(request):
    return request.session.get(CART_SESSION_KEY, {})


def _set_session_cart(request, cart):
    request.session[CART_SESSION_KEY] = cart
    request.session.modified = True

def _merge_session_cart(request, user):
    raw_cart = _get_session_cart(request)
    if raw_cart:
        cart, _ = Cart.objects.get_or_create(user=user)
        for pid, quantity in raw_cart.items():
            qty = int(quantity)
            if qty > 0:
                try:
                    product = BaseProduct.objects.get(id=pid)
                    cart_item, created = CartItem.objects.get_or_create(
                        cart=cart, product=product,
                        defaults={'quantity': qty}
                    )
                    if not created:
                        cart_item.quantity += qty
                        cart_item.save(update_fields=['quantity'])
                except BaseProduct.DoesNotExist:
                    continue
        if CART_SESSION_KEY in request.session:
            del request.session[CART_SESSION_KEY]
            request.session.modified = True

def _build_cart_items(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        items = CartItem.objects.select_related('product').filter(cart=cart, product__is_active=True)

        cart_items = []
        total = Decimal('0.00')
        cart_count = 0

        for item in items:
            qty = int(item.quantity)
            if qty <= 0:
                continue

            subtotal = item.product.price * qty
            total += subtotal
            cart_count += qty
            image_url = item.product.image.url if item.product.image else PLACEHOLDER_IMAGE

            cart_items.append({
                'product': item.product,
                'quantity': qty,
                'subtotal': subtotal,
                'image_url': image_url,
            })

        return cart_items, total, cart_count

    raw_cart = _get_session_cart(request)
    if not raw_cart:
        return [], Decimal('0.00'), 0

    product_ids = []
    for pid in raw_cart.keys():
        try:
            product_ids.append(uuid.UUID(str(pid)))
        except (ValueError, TypeError):
            continue

    products = {
        str(product.id): product
        for product in BaseProduct.objects.filter(id__in=product_ids, is_active=True)
    }

    cart_items = []
    total = Decimal('0.00')
    cart_count = 0

    
    for pid, quantity in raw_cart.items():
        product = products.get(str(pid))
        if not product:
            continue

        try:
            qty = int(quantity)
        except (TypeError, ValueError):
            continue

        if qty <= 0:
            continue

        subtotal = product.price * qty
        total += subtotal
        cart_count += qty
        image_url = product.image.url if product.image else PLACEHOLDER_IMAGE

        cart_items.append({
            'product': product,
            'quantity': qty,
            'subtotal': subtotal,
            'image_url': image_url,
        })

    return cart_items, total, cart_count


@ensure_csrf_cookie
def main(request):
    selected_category_id = request.GET.get('category')

    products_qs = (
        BaseProduct.objects
        .filter(is_active=True)
        .select_related('category_link__category')
        .prefetch_related('extra_images')
    )

    if selected_category_id and selected_category_id.isdigit():
        products_qs = products_qs.filter(category_link__category_id=int(selected_category_id))
    else:
        selected_category_id = ''

    # Paginação
    page = int(request.GET.get('page', 1))
    per_page = 12
    total_products = products_qs.count()
    total_pages = (total_products + per_page - 1) // per_page
    products_page = products_qs[(page-1)*per_page:page*per_page]
    products = list(products_page)

    for product in products:
        carousel_images = _get_product_images(product)
        product.carousel_images = carousel_images
        product.cover_image = carousel_images[0]

    destaques = list(products_qs[:8]) if products_qs.exists() else []

    for product in destaques:
        if not hasattr(product, 'carousel_images') or not product.carousel_images:
            carousel_images = _get_product_images(product)
            product.carousel_images = carousel_images
            product.cover_image = carousel_images[0] if carousel_images else PLACEHOLDER_IMAGE
    brigadeiro_products = list(
        BaseProduct.objects
        .filter(is_active=True, category_link__category__name__icontains='brigadeiro')
        .select_related('category_link__category')
        .prefetch_related('extra_images')
        .order_by('name')
    )

    for product in brigadeiro_products:
        carousel_images = _get_product_images(product)
        product.cover_image = carousel_images[0]

    total_active_products = BaseProduct.objects.filter(is_active=True).count()
    store_stats = StoreStat.get_solo()
    categories = Category.objects.annotate(
        item_count=Count('products', filter=Q(products__product__is_active=True))
    ).order_by('name')
    page_numbers = list(range(1, total_pages+1)) if total_pages > 1 else []
    context = {
        'products': products,
        'categories': categories,
        'total_active_products': total_active_products,
        'stats': store_stats,
        'destaques': destaques,
        'selected_category_id': str(selected_category_id),
        'brigadeiro_products': brigadeiro_products,
        'page': page,
        'total_pages': total_pages,
        'total_products': total_products,
        'per_page': per_page,
        'page_numbers': page_numbers,
    }
    return render(request, 'stand/main.html', context)

def cart(request):
    pending_order = None
    if request.user.is_authenticated:
        pending_order = (
            Order.objects
            .filter(client=request.user, status='pending', payment_status=False)
            .order_by('-created_at')
            .first()
        )
        
    cart_items, cart_total, cart_count = _build_cart_items(request)
    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'cart_count': cart_count,
        'pending_order': pending_order,
    }
    return render(request, 'stand/cart.html', context)


import json

@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(BaseProduct, pk=product_id, is_active=True)
    quantity_to_add = 1
    try:
        
        if request.body:
            data = json.loads(request.body)
            quantity_to_add = int(data.get('quantity', 1))
    except Exception:
        pass
        
    if quantity_to_add < 1:
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            cart_count = sum(int(item.quantity) for item in cart.items.all())
        else:
            cart = _get_session_cart(request)
            cart_count = 0
            for value in cart.values():
                try:
                    cart_count += int(value)
                except (TypeError, ValueError):
                    continue

        return JsonResponse({
            'ok': True,
            'ignored': True,
            'product_id': product.id,
            'product_name': product.name,
            'quantity': 0,
            'cart_count': cart_count,
        })

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity_to_add},
        )
        if not created:
            cart_item.quantity += quantity_to_add
            cart_item.save(update_fields=['quantity'])
        quantity = int(cart_item.quantity)
        cart_count = sum(int(item.quantity) for item in cart.items.all())
    else:
        cart = _get_session_cart(request)
        key = str(product.id)
        cart[key] = int(cart.get(key, 0)) + quantity_to_add
        _set_session_cart(request, cart)

        quantity = int(cart[key])
        cart_count = 0
        for value in cart.values():
            try:
                cart_count += int(value)
            except (TypeError, ValueError):
                continue

    return JsonResponse({
        'ok': True,
        'product_id': product.id,
        'product_name': product.name,
        'quantity': quantity,
        'cart_count': cart_count,
    })


@require_POST

def remove_from_cart(request, product_id):
    product = get_object_or_404(BaseProduct, pk=product_id)
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        CartItem.objects.filter(cart=cart, product=product).delete()
    else:
        cart = _get_session_cart(request)
        key = str(product.id)
        if key in cart:
            del cart[key]
            _set_session_cart(request, cart)
            
    return redirect('stand:cart')

def add_custom_brigadeiro_hundred(request):

    try:
        payload = json.loads(request.body or '{}')
    except Exception:
        return JsonResponse({'ok': False, 'error': 'Dados invalidos.'}, status=400)

    raw_product_ids = payload.get('product_ids', None)
    if raw_product_ids is None:
        raw_items = payload.get('items', [])
        if not isinstance(raw_items, list):
            return JsonResponse({'ok': False, 'error': 'Formato de itens invalido.'}, status=400)
        raw_product_ids = []
        for raw_item in raw_items:
            if not isinstance(raw_item, dict):
                return JsonResponse({'ok': False, 'error': 'Item invalido informado.'}, status=400)
            raw_product_ids.append(raw_item.get('product_id', ''))

    if not isinstance(raw_product_ids, list):
        return JsonResponse({'ok': False, 'error': 'Formato de sabores invalido.'}, status=400)

    product_ids = []
    seen_ids = set()

    for raw_product_id in raw_product_ids:
        product_id = str(raw_product_id or '').strip()
        try:
            uuid.UUID(product_id)
        except (ValueError, TypeError):
            return JsonResponse({'ok': False, 'error': 'Identificador de sabor invalido.'}, status=400)

        if not product_id:
            return JsonResponse({'ok': False, 'error': 'Selecione sabores validos.'}, status=400)

        if product_id in seen_ids:
            return JsonResponse({'ok': False, 'error': 'Nao repita o mesmo sabor no cento personalizado.'}, status=400)

        seen_ids.add(product_id)
        product_ids.append(product_id)

    if len(product_ids) not in (2, 3):
        return JsonResponse({'ok': False, 'error': 'Escolha exatamente 2 ou 3 sabores diferentes.'}, status=400)

    quantities = [50, 50] if len(product_ids) == 2 else [33, 33, 34]
    parsed_items = [
        {'product_id': product_ids[index], 'quantity': quantities[index]}
        for index in range(len(product_ids))
    ]
    total_units = sum(quantities)

    valid_products = {
        str(product.id): product
        for product in BaseProduct.objects.filter(
            id__in=product_ids,
            is_active=True,
            category_link__category__name__icontains='brigadeiro',
        )
    }

    if len(valid_products) != len(product_ids):
        return JsonResponse({'ok': False, 'error': 'Um ou mais sabores selecionados nao sao validos para brigadeiro.'}, status=400)

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        for item in parsed_items:
            product = valid_products[item['product_id']]
            quantity = item['quantity']
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity},
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save(update_fields=['quantity'])

        cart_count = sum(int(item.quantity) for item in cart.items.all())
    else:
        session_cart = _get_session_cart(request)
        for item in parsed_items:
            product_id = item['product_id']
            session_cart[product_id] = int(session_cart.get(product_id, 0)) + item['quantity']
        _set_session_cart(request, session_cart)

        cart_count = 0
        for value in session_cart.values():
            try:
                cart_count += int(value)
            except (TypeError, ValueError):
                continue

    custom_total = Decimal('0.00')
    for item in parsed_items:
        product = valid_products[item['product_id']]
        custom_total += product.price * item['quantity']

    return JsonResponse({
        'ok': True,
        'cart_count': cart_count,
        'units': total_units,
        'custom_total': f'{custom_total:.2f}',
        'distribution': quantities,
    })

import random
from django.utils import timezone
import resend
from django.conf import settings

def login(request):
    raw_next = request.POST.get('next') or request.GET.get('next') or ''
    next_url = ''
    if url_has_allowed_host_and_scheme(raw_next, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        next_url = raw_next

    if request.user.is_authenticated:
        if next_url:
            return redirect(next_url)
        return redirect('stand:main')

    if request.method == 'POST':
        import nh3
        username = nh3.clean(request.POST.get('username', ''), tags=set())
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:

            
            otp = str(uuid.uuid4().int)[:6]
            request.session['pending_2fa_otp'] = otp
            request.session['pending_2fa_timestamp'] = timezone.now().isoformat()
            
            try:
                resend.api_key = settings.RESEND_API_KEY
                resend.Emails.send({
                    "from": "Arte & Sabor <nao-responda@seatechcorp.com.br>",
                    "to": [user.email],
                    "subject": "Seu código de verificação (2FA)",
                    "html": f"<p>Seu código é: <strong>{otp}</strong></p>"
                })
            except Exception as e:
                messages.error(request, f"Erro ao enviar email 2FA")
                return redirect('stand:login')
            
            request.session['pending_2fa_user_id'] = str(user.id)
            if next_url:
                request.session['pending_2fa_next_url'] = next_url
            return redirect('stand:verify_2fa')
        else:
            messages.error(request, "Usuário ou senha incorretos.")

    context = {
        'next_url': next_url,
    }
    return render(request, 'stand/login.html', context)

def verify_2fa(request):
    user_id = request.session.get('pending_2fa_user_id')
    if not user_id:
        return redirect('stand:login')
        
    if request.method == 'POST':
        otp_code = request.POST.get('otp_code', '').strip()
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return redirect('stand:login')
            
        pending_otp = request.session.get('pending_2fa_otp')
        pending_timestamp_str = request.session.get('pending_2fa_timestamp')
        
        if pending_otp and pending_otp == otp_code:
            
            if pending_timestamp_str:
                import datetime
                pending_timestamp = datetime.datetime.fromisoformat(pending_timestamp_str)
                diff = timezone.now() - pending_timestamp
                if diff.total_seconds() > 600:
                    messages.error(request, "Código expirado.")
                    return render(request, 'stand/verify_2fa.html')
            
            auth_login(request, user)
            _merge_session_cart(request, user)
            del request.session['pending_2fa_user_id']
            if 'pending_2fa_otp' in request.session:
                del request.session['pending_2fa_otp']
            if 'pending_2fa_timestamp' in request.session:
                del request.session['pending_2fa_timestamp']
                
            next_url = request.session.pop('pending_2fa_next_url', '')
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
                return redirect(next_url)
            return redirect('stand:main')
        else:
            messages.error(request, "Código inválido.")
            
    return render(request, 'stand/verify_2fa.html')

def register(request):
    if request.user.is_authenticated:
        return redirect('stand:main')
        
    if request.method == 'POST':
        import nh3
        name = nh3.clean(request.POST.get('name', ''), tags=set())
        username = nh3.clean(request.POST.get('username', ''), tags=set())
        email = nh3.clean(request.POST.get('email', ''), tags=set())
        phone = nh3.clean(request.POST.get('phone', ''), tags=set())
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "As senhas não coincidem.")
            return render(request, 'stand/register.html')

        try:
            validate_password(password, user=User(username=username, email=email))
        except ValidationError as exc:
            for error in exc.messages:
                messages.error(request, error)
            return render(request, 'stand/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Este nome de usuário já está em uso.")
            return render(request, 'stand/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Este email já está cadastrado.")
            return render(request, 'stand/register.html')

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )
            
            if name:
                user.name = name
            if phone:
                user.phone = phone
            user.save()

            
            auth_login(request, user)
            _merge_session_cart(request, user)
            return redirect('stand:main')
            
        except Exception as e:
            messages.error(request, f"Erro ao criar conta: {str(e)}")
            return render(request, 'stand/register.html')

    return render(request, 'stand/register.html')

@login_required(login_url='stand:login')
def profile(request):
    if request.method == 'POST':
        import nh3
        user = request.user
        
        
        name = nh3.clean(request.POST.get('name', ''), tags=set())
        phone = nh3.clean(request.POST.get('phone', ''), tags=set())
        birth_date = nh3.clean(request.POST.get('birth_date', ''), tags=set())
        if name:
            user.name = name
        if phone:
            user.phone = phone
        if birth_date:
            user.birth_date = birth_date
            
        try:
            user.save()
            messages.success(request, 'Dados atualizados com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao atualizar dados: {str(e)}')
            
        return redirect('stand:profile')

    orders = Order.objects.filter(client=request.user).order_by('-created_at')[:10]
    
    context = {'orders': orders}
    return render(request, 'stand/profile.html', context)

def user_logout(request):
    auth_logout(request)
    return redirect('stand:login')

@login_required(login_url='stand:login')
def profile_addresses(request):
    if request.method == 'POST':
        import nh3
        action = request.POST.get('action')
        
        if action == 'delete':
            address_id = request.POST.get('address_id')
            try:
                address = Address.objects.get(id=address_id, user=request.user)
                address.delete()
                messages.success(request, 'Endereço removido com sucesso!')
            except Address.DoesNotExist:
                messages.error(request, 'Endereço não encontrado.')
                
        elif action == 'create':
            street = nh3.clean(request.POST.get('street', ''), tags=set())
            number = request.POST.get('number', 0)
            city = nh3.clean(request.POST.get('city', ''), tags=set())
            state = nh3.clean(request.POST.get('state', ''), tags=set())
            zip_code = nh3.clean(request.POST.get('zip_code', ''), tags=set())
            
            try:
                Address.objects.create(
                    user=request.user,
                    street=street,
                    number=number,
                    city=city,
                    state=state,
                    zip_code=zip_code
                )
                messages.success(request, 'Novo endereço cadastrado com sucesso!')
            except Exception as e:
                messages.error(request, f'Erro ao cadastrar endereço: {str(e)}')
                
        return redirect('stand:profile_addresses')

    addresses = Address.objects.filter(user=request.user)
    context = {'addresses': addresses}
    return render(request, 'stand/profile_addresses.html', context)
from artesabor.pagbank import create_pix_order

@login_required(login_url='stand:login')
def pay_pending_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, client=request.user, status='pending', payment_status=False)
    
    if request.method == 'POST':
        action = request.POST.get('action', 'pay')

        if action == 'cancel':
            order.delete()
            messages.success(request, 'Pedido pendente cancelado com sucesso.')
            return redirect('stand:cart')

        order_items = list(order.items.select_related('product').all())
        has_invalid_quantity = False
        
        for item in order_items:
            field_name = f'item_qty_{item.id}'
            raw_qty = request.POST.get(field_name, str(item.quantity))
            try:
                quantity = int(raw_qty)
            except (TypeError, ValueError):
                has_invalid_quantity = True
                break

            if quantity < 0:
                has_invalid_quantity = True
                break

            if quantity == 0:
                item.delete()
                continue

            if quantity != item.quantity:
                item.quantity = quantity
                item.save(update_fields=['quantity'])

        if has_invalid_quantity:
            messages.error(request, 'Informe apenas quantidades válidas (0 ou maior).')
            return redirect('stand:cart')

        if order.items.count() == 0:
            order.delete()
            messages.error(request, 'O pedido ficou vazio e foi cancelado.')
            return redirect('stand:cart')
            
        pix_response = create_pix_order(order, order.items.all(), request.user)
        if pix_response.get('success'):
            qr_codes = pix_response.get('qr_codes', [])
            qr_code_link = qr_codes[0].get('links', [{}])[0].get('href') if qr_codes else ''
            qr_text = qr_codes[0].get('text') if qr_codes else ''
            return render(request, 'stand/checkout_pix.html', {'order': order, 'qr_code_link': qr_code_link, 'qr_text': qr_text})
        else:
            messages.error(request, 'Erro ao gerar PIX: ' + str(pix_response.get('error', 'Desconhecido')))
            return redirect('stand:cart')
            
    return redirect('stand:cart')

def checkout(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            request.session['checkout_selected_items'] = request.POST.getlist('selected_items')
            request.session.modified = True

        login_url = reverse('stand:login')
        checkout_url = reverse('stand:checkout')
        return redirect(f"{login_url}?{urlencode({'next': checkout_url})}")

    cart_items, _, _ = _build_cart_items(request)
    if not cart_items:
        messages.error(request, 'Seu carrinho esta vazio.')
        return redirect('stand:cart')

    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_items')
        schedule_order = request.POST.get('schedule_order') == '1'
    else:
        selected_ids = request.session.pop('checkout_selected_items', [])
        schedule_order = False
        request.session.modified = True

    if not selected_ids:
        messages.error(request, 'Selecione ao menos um item para comprar.')
        return redirect('stand:cart')

    selected_cart_items = []
    for item in cart_items:
        p = item['product'] if isinstance(item, dict) else item.product
        if str(p.id) in selected_ids:
            selected_cart_items.append(item)

    if not selected_cart_items:
        messages.error(request, 'Nenhum item valido selecionado.')
        return redirect('stand:cart')

    pending_order = (
        Order.objects
        .filter(client=request.user, status='pending', payment_status=False)
        .order_by('-created_at')
        .first()
    )

    if pending_order:
        order = pending_order
    else:
        order = Order.objects.create(client=request.user, status='pending')

    for item in selected_cart_items:
        p = item['product'] if isinstance(item, dict) else item.product
        q = item['quantity'] if isinstance(item, dict) else item.quantity
        order_item, created = OrderItem.objects.get_or_create(
            order=order,
            product=p,
            defaults={'quantity': q},
        )
        if not created:
            order_item.quantity += q
            order_item.save(update_fields=['quantity'])

    if schedule_order:
        for item in selected_cart_items:
            p = item['product'] if isinstance(item, dict) else item.product
            CartItem.objects.filter(cart__user=request.user, product=p).delete()
        return render(request, 'stand/schedule_confirm.html', {'order': order})

    pix_response = create_pix_order(order, order.items.select_related('product').all(), request.user)
    if pix_response.get('success'):
        for item in selected_cart_items:
            p = item['product'] if isinstance(item, dict) else item.product
            CartItem.objects.filter(cart__user=request.user, product=p).delete()

        qr_codes = pix_response.get('qr_codes', [])
        qr_code_link = qr_codes[0].get('links', [{}])[0].get('href') if qr_codes else ''
        qr_text = qr_codes[0].get('text') if qr_codes else ''
        return render(request, 'stand/checkout_pix.html', {'order': order, 'qr_code_link': qr_code_link, 'qr_text': qr_text})

    order.delete()
    messages.error(request, 'Erro ao gerar PIX: ' + str(pix_response.get('error', 'Desconhecido')))
    return redirect('stand:cart')
