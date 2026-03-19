import nh3
from base.models import BaseProduct, ProductVariation, Cart, CartItem, BaseCustomUser, UserSecurityProfile, Order, OrderItem
from django import forms

class BaseSanitizedModelForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        for field_name, value in cleaned_data.items():
            if isinstance(value, str):
                cleaned_data[field_name] = nh3.clean(value, tags=set())
        return cleaned_data

class ProductForm(BaseSanitizedModelForm):
    class Meta: 
        model = BaseProduct
        fields = "__all__"

class ProductVariationForm(BaseSanitizedModelForm):
    class Meta:
        model = ProductVariation
        fields = "__all__"

class CartForm(BaseSanitizedModelForm):
    class Meta:
        model = Cart
        fields = "__all__"

class CartItemForm(BaseSanitizedModelForm):
    class Meta:
        model = CartItem
        fields = "__all__"

class BaseUserForm(BaseSanitizedModelForm):
    class Meta:
        model = BaseCustomUser
        fields = "__all__"

class UserSecurityForm(BaseSanitizedModelForm):
    class Meta:
        model = UserSecurityProfile
        fields = "__all__"

class OrderForm(BaseSanitizedModelForm):
    class Meta:
        model = Order
        fields = "__all__"

class OrderItem(BaseSanitizedModelForm):
    class Meta:
        model = OrderItem
        fields = "__all__"


