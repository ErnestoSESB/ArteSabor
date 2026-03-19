from django.db import models 
from django.conf import settings 
from base.models import BaseProduct 
 
class ProductClick(models.Model): 
    product = models.ForeignKey(BaseProduct, on_delete=models.CASCADE, related_name='crm_clicks') 
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL) 
    created_at = models.DateTimeField(auto_now_add=True) 
