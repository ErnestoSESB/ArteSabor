from django import forms
from django.forms import inlineformset_factory
from stand.forms import BaseSanitizedModelForm
from base.models import BaseProduct, ProductVariation, Order, OrderItem
from .models import Category, ProductCategoryLink, StoreStat
import nh3


class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean

        if isinstance(data, (list, tuple)):
            cleaned = [single_file_clean(d, initial) for d in data if d]
        else:
            cleaned = [single_file_clean(data, initial)] if data else []

        return cleaned


class ProductForm(BaseSanitizedModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label='Categoria',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    extra_images = MultipleFileField(
        required=False,
        label='Imagens adicionais (máx. 6)',
        widget=MultipleFileInput(attrs={'class': 'form-control', 'multiple': True})
    )

    class Meta: 
        model = BaseProduct
        fields = ['name', 'price', 'description', 'stock', 'image', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Brigadeiro Gourmet'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            try:
                self.fields['category'].initial = self.instance.category_link.category
            except ProductCategoryLink.DoesNotExist:
                pass

    def clean_name(self):
        return nh3.clean(self.cleaned_data.get('name', ''), tags=set())

    def clean_description(self):
        value = self.cleaned_data.get('description') or ''
        return nh3.clean(value, tags=set())

    def clean_extra_images(self):
        files = self.cleaned_data.get('extra_images') or []
        existing_count = self.instance.extra_images.count() if self.instance and self.instance.pk else 0

        if existing_count + len(files) > 6:
            raise forms.ValidationError('Você pode ter no máximo 6 imagens adicionais por produto.')

        return files


class ProductVariationForm(BaseSanitizedModelForm):
    class Meta:
        model = ProductVariation
        fields = '__all__'


class CategoryForm(BaseSanitizedModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Brigadeiros'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descrição opcional'}),
        }

    def clean_name(self):
        return nh3.clean(self.cleaned_data.get('name', ''), tags=set())

    def clean_description(self):
        return nh3.clean(self.cleaned_data.get('description', ''), tags=set())

class StoreStatForm(BaseSanitizedModelForm):
    class Meta:
        model = StoreStat
        fields = ['happy_customers', 'pastries_sold', 'years_experience', 'exclusive_recipes']
        widgets = {
            'happy_customers': forms.NumberInput(attrs={'class': 'form-control'}),
            'pastries_sold': forms.NumberInput(attrs={'class': 'form-control'}),
            'years_experience': forms.NumberInput(attrs={'class': 'form-control'}),
            'exclusive_recipes': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class OrderForm(BaseSanitizedModelForm):
    class Meta:
        model = Order
        fields = ['client', 'status']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'})
        }

class OrderItemERPForm(BaseSanitizedModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']

OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemERPForm,
    extra=1,
    can_delete=True,
    widgets={
        'product': forms.Select(attrs={'class': 'form-control'}),
        'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'})
    }
)
