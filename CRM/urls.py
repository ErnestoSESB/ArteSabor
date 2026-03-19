from django.urls import path
from . import views

app_name = 'CRM'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('relationship/', views.relationship, name='relationship'),
    path('track_click/', views.track_product_click, name='track_click'),
]
