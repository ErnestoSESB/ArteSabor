from django.urls import path
from . import views

app_name = 'stand'

urlpatterns = [
    path('', views.main, name='main'),
    path('cart/', views.cart, name='cart'),
    path('cart/add/<uuid:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<uuid:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/add-custom-hundred/', views.add_custom_brigadeiro_hundred, name='add_custom_brigadeiro_hundred'),
    path('checkout/', views.checkout, name='checkout'),
    path('pay-pending-order/<uuid:order_id>/', views.pay_pending_order, name='pay_pending_order'),
    path('login/', views.login, name='login'),
    path('verify-2fa/', views.verify_2fa, name='verify_2fa'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/addresses/', views.profile_addresses, name='profile_addresses'),
]

