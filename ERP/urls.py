from django.urls import path
from . import views

app_name = 'ERP'

urlpatterns = [
    path('', views.Adminview, name='admin'),
    path('estatisticas/editar/', views.edit_store_stats, name='edit_store_stats'),
    path('produto/novo/', views.create_product, name='create_product'),
    path('produto/<uuid:pk>/editar/', views.edit_product, name='editar_doce'),
    path('produto/<uuid:pk>/excluir/', views.delete_product, name='excluir_doce'),
    path('pedido/novo/', views.create_order, name='create_order'),
    path('categoria/nova/', views.create_category, name='create_category'),
    path('categoria/<int:pk>/editar/', views.edit_category, name='editar_categoria'),
    path('categoria/<int:pk>/excluir/', views.delete_category, name='excluir_categoria'),
    path('receita/nova/', views.create_recipe, name='create_recipe'),
    path('receita/<int:pk>/editar/', views.edit_recipe, name='edit_recipe'),
    path('receita/<int:pk>/excluir/', views.delete_recipe, name='delete_recipe'),
    path('finance/add_cash/', views.finance_add_cash, name='finance_add_cash'),
    path('finance/remove_cash/', views.finance_remove_cash, name='finance_remove_cash'),
    path('finance/add_loan/', views.finance_add_loan, name='finance_add_loan'),
    path('finance/remove_loan/', views.finance_remove_loan, name='finance_remove_loan'),
]
