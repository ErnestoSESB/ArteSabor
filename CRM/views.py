from django.shortcuts import render
from django.db.models import Count
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from decimal import Decimal
import json
from base.models import Order
from .models import ProductClick

def is_staff_check(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_staff_check, login_url='stand:login')
def dashboard(request):
    top_clicks = ProductClick.objects.values('product__name').annotate(
        click_count=Count('id')
    ).order_by('-click_count')[:10]

    recent_clicks = ProductClick.objects.select_related('product', 'user').order_by('-created_at')[:8]

    total_clicks = ProductClick.objects.count()

    context = {
        'active_page': 'funnel',
        'top_clicks': top_clicks,
        'recent_clicks': recent_clicks,
        'total_clicks': total_clicks
    }
    return render(request, 'CRM/dashboard.html', context)

def _get_order_total(order):
    total_attr = getattr(order, 'get_total', None)
    if callable(total_attr):
        return total_attr() or Decimal('0.00')
    if total_attr is None:
        return Decimal('0.00')
    return total_attr

@user_passes_test(is_staff_check, login_url='stand:login')
def relationship(request):
    orders = (
        Order.objects
        .select_related('client')
        .prefetch_related('items')
        .order_by('-created_at')
    )

    customers_map = {}
    for order in orders:
        client = order.client
        if client is None:
            continue

        client_id = client.pk
        if client_id not in customers_map:
            address = client.addresses.first()
            city = address.city if address and address.city else 'Não informado'
            state = address.state if address and address.state else '--'
            customers_map[client_id] = {
                'client': client,
                'id': client_id,
                'display_name': client.get_full_name() or client.username,
                'email': client.email,
                'city': city,
                'state': state,
                'ltv': Decimal('0.00'),
                'orders_count': 0,
                'is_active': client.is_active,
                'orders': [],
            }

        customers_map[client_id]['orders'].append(order)
        customers_map[client_id]['orders_count'] += 1
        customers_map[client_id]['ltv'] += _get_order_total(order)

    customers = list(customers_map.values())
    customers.sort(key=lambda c: c['ltv'], reverse=True)

    return render(
        request,
        'CRM/dashboard.html',
        {
            'active_page': 'relationship',
            'customers': customers,
        },
    )

def track_product_click(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            if product_id:
                ProductClick.objects.create(
                    product_id=product_id,
                    user=request.user if request.user.is_authenticated else None
                )
                return JsonResponse({'status': 'ok'})
        except Exception as e:
            pass
    return JsonResponse({'status': 'error'}, status=400)
