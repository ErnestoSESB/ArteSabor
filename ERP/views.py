from .models import FinanceBox, FinanceLog
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.db.models import Count
from decimal import Decimal
from base.models import BaseProduct, Order
from .models import Category, StoreStat, ProductCategoryLink, ProductImage, Recipe
from .forms import CategoryForm, StoreStatForm, ProductForm, OrderForm, OrderItemFormSet

def is_staff_check(user):
    return user.is_authenticated and user.is_staff


def _get_client_number(client):
    for attr in ('phone', 'phone_number', 'number', 'numero', 'mobile', 'cellphone', 'whatsapp'):
        value = getattr(client, attr, None)
        if value:
            return str(value)
    return 'Nao informado'


def _get_client_display_name(client):
    get_full_name = getattr(client, 'get_full_name', None)
    if callable(get_full_name):
        full_name = (get_full_name() or '').strip()
        if full_name:
            return full_name
    for attr in ('username', 'email', 'id'):
        value = getattr(client, attr, None)
        if value:
            return str(value)
    return 'Cliente sem identificacao'


@user_passes_test(is_staff_check, login_url='stand:login')
def Adminview(request):
    doces = BaseProduct.objects.all()
    categories = Category.objects.all()
    stats = StoreStat.get_solo()
    orders = (
        Order.objects
        .select_related('client')
        .prefetch_related('items__product')
        .all()
        .order_by('-created_at')
    )
    recipes = Recipe.objects.prefetch_related('ingredients').all()

    User = get_user_model()
    clients_qs = User.objects.filter(is_staff=False)

    user_fields = {field.name for field in User._meta.get_fields()}
    if 'date_joined' in user_fields:
        clients_qs = clients_qs.order_by('-date_joined')
    else:
        clients_qs = clients_qs.order_by('-id')

    orders_count_by_client = {
        item['client']: item['orders_count']
        for item in (
            Order.objects
            .values('client')
            .annotate(orders_count=Count('id'))
        )
    }

    customers = []
    for client in clients_qs:
        address = client.addresses.first()
        city = address.city if address and address.city else 'Não informado'
        state = address.state if address and address.state else '--'
        customers.append({
            'client': client,
            'display_name': _get_client_display_name(client),
            'number': _get_client_number(client),
            'email': getattr(client, 'email', '') or 'Nao informado',
            'date_joined': getattr(client, 'date_joined', None),
            'orders_count': orders_count_by_client.get(client.id, 0),
            'last_login': getattr(client, 'last_login', None),
            'city': city,
            'state': state,
        })

    payment_logs = []
    paid_total_value = Decimal('0.00')
    pending_total_value = Decimal('0.00')
    context = {}

    for order in orders:
        order_total = order.get_total
        is_paid = bool(order.payment_status)
        client = order.client
        client_name = _get_client_display_name(client) if client else 'Cliente removido'
        client_email = getattr(client, 'email', '') if client else ''

        payment_logs.append({
            'order': order,
            'client_name': client_name,
            'client_email': client_email or 'Nao informado',
            'is_paid': is_paid,
            'payment_label': 'Realizado' if is_paid else 'Pendente',
            'total': order_total,
            'event_date': order.updated_at if is_paid else order.created_at,
        })

        if is_paid:
            paid_total_value += order_total
        else:
            pending_total_value += order_total

        # Adiciona finance_box e finance_logs ao context
        finance_box = FinanceBox.get_solo()
        finance_logs = FinanceLog.objects.filter(box=finance_box)[:10]
        context['finance_box'] = finance_box
        context['finance_logs'] = finance_logs
    paid_payments_count = sum(1 for log in payment_logs if log['is_paid'])
    pending_payments_count = len(payment_logs) - paid_payments_count

    context.update({
        'doces': doces,
        'categories': categories,
        'stats': stats,
        'orders': orders,
        'customers': customers,
        'recipes': recipes,
        'payment_logs': payment_logs,
        'paid_payments_count': paid_payments_count,
        'pending_payments_count': pending_payments_count,
        'paid_total_value': paid_total_value,
        'pending_total_value': pending_total_value,
    })
    return render(request, 'ERP/admin.html', context)

@user_passes_test(is_staff_check, login_url='stand:login')
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            category = form.cleaned_data.get('category')
            if category:
                ProductCategoryLink.objects.create(product=product, category=category)
            
            extra_images = form.cleaned_data.get('extra_images')
            if extra_images:
                for img in extra_images:
                    ProductImage.objects.create(product=product, image=img)
            return redirect('ERP:admin')
    else:
        form = ProductForm()
    return render(request, 'ERP/product_form.html', {'form': form})

@user_passes_test(is_staff_check, login_url='stand:login')
def edit_product(request, pk):
    product = get_object_or_404(BaseProduct, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            category = form.cleaned_data.get('category')
            if category:
                link, created = ProductCategoryLink.objects.get_or_create(product=product, defaults={'category': category})
                if not created and link.category != category:
                    link.category = category
                    link.save()
            else:
                ProductCategoryLink.objects.filter(product=product).delete()
            
            extra_images = form.cleaned_data.get('extra_images')
            if extra_images:
                for img in extra_images:
                    ProductImage.objects.create(product=product, image=img)
            return redirect('ERP:admin')
    else:
        form = ProductForm(instance=product)
    
    existing_images = product.extra_images.all()
    return render(request, 'ERP/product_form.html', {'form': form, 'existing_images': existing_images})

@user_passes_test(is_staff_check, login_url='stand:login')
def delete_product(request, pk):
    product = get_object_or_404(BaseProduct, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('ERP:admin')
    return render(request, 'ERP/confirm_delete.html', {'doce': product})

@user_passes_test(is_staff_check, login_url='stand:login')
def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        formset = OrderItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            order = form.save()
            instances = formset.save(commit=False)
            for instance in instances:
                instance.order = order
                instance.save()
            for deleted in formset.deleted_objects:
                deleted.delete()
            return redirect('ERP:admin')
    else:
        form = OrderForm()
        formset = OrderItemFormSet()
    
    return render(request, 'ERP/order_form.html', {'form': form, 'formset': formset})

@user_passes_test(is_staff_check, login_url='stand:login')
def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ERP:admin')
    else:
        form = CategoryForm()
    return render(request, 'ERP/category_form.html', {'form': form})

@user_passes_test(is_staff_check, login_url='stand:login')
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('ERP:admin')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'ERP/category_form.html', {'form': form})

@user_passes_test(is_staff_check, login_url='stand:login')
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('ERP:admin')
    return render(request, 'ERP/category_confirm_delete.html', {'category': category})

@user_passes_test(is_staff_check, login_url='stand:login')
def edit_store_stats(request):
    stats = StoreStat.get_solo()
    if request.method == 'POST':
        form = StoreStatForm(request.POST, instance=stats)
        if form.is_valid():
            form.save()
            return redirect('ERP:admin')
    else:
        form = StoreStatForm(instance=stats)
    return render(request, 'ERP/stats_form.html', {'form': form})

from .recipe_views import create_recipe, edit_recipe, delete_recipe

from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt

@user_passes_test(is_staff_check, login_url='stand:login')
@csrf_exempt
def finance_add_cash(request):
    if request.method == 'POST':
        box = FinanceBox.get_solo()
        value = Decimal(request.POST.get('value', '0'))
        box.cash_total += value
        box.save()
        FinanceLog.objects.create(box=box, action='add_cash', value=value, description='Adicionado ao caixa')
    return redirect('ERP:admin')

@user_passes_test(is_staff_check, login_url='stand:login')
@csrf_exempt
def finance_remove_cash(request):
    if request.method == 'POST':
        box = FinanceBox.get_solo()
        value = Decimal(request.POST.get('value', '0'))
        box.cash_total -= value
        box.save()
        FinanceLog.objects.create(box=box, action='remove_cash', value=value, description='Removido do caixa')
    return redirect('ERP:admin')

@user_passes_test(is_staff_check, login_url='stand:login')
@csrf_exempt
def finance_add_loan(request):
    if request.method == 'POST':
        box = FinanceBox.get_solo()
        value = Decimal(request.POST.get('value', '0'))
        box.loan_total += value
        box.save()
        FinanceLog.objects.create(box=box, action='add_loan', value=value, description='Adicionado ao empréstimo')
    return redirect('ERP:admin')

@user_passes_test(is_staff_check, login_url='stand:login')
@csrf_exempt
def finance_remove_loan(request):
    if request.method == 'POST':
        box = FinanceBox.get_solo()
        value = Decimal(request.POST.get('value', '0'))
        box.loan_total -= value
        box.save()
        FinanceLog.objects.create(box=box, action='remove_loan', value=value, description='Removido do empréstimo')
    return redirect('ERP:admin')
