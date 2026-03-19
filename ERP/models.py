from django.db import models
class FinanceBox(models.Model):
    cash_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    loan_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = 'Caixa Financeiro'
        verbose_name_plural = 'Caixas Financeiros'
    def __str__(self):
        return f"Caixa: R$ {self.cash_total} | Empréstimo: R$ {self.loan_total}"
    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj
    
class FinanceLog(models.Model):
    box = models.ForeignKey(FinanceBox, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=32) 
    value = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True)
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Log Financeiro'
        verbose_name_plural = 'Logs Financeiros'
    def __str__(self):
        return f"{self.action} R$ {self.value} em {self.created_at:%d/%m/%Y %H:%M}"
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

    def __str__(self):
        return self.name

class ProductCategoryLink(models.Model):
    product = models.OneToOneField('base.BaseProduct', on_delete=models.CASCADE, related_name='category_link')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    def __str__(self):
        return f"{self.product.name} -> {self.category.name if self.category else 'Sem categoria'}"

class ProductImage(models.Model):
    product = models.ForeignKey('base.BaseProduct', on_delete=models.CASCADE, related_name='extra_images')
    image = models.ImageField(upload_to='products/')
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Imagem {self.order} - {self.product.name}"

class StoreStat(models.Model):
    happy_customers = models.PositiveIntegerField(default=2500, verbose_name="Clientes Felizes")
    pastries_sold = models.PositiveIntegerField(default=15000, verbose_name="Doces Vendidos")
    years_experience = models.PositiveIntegerField(default=8, verbose_name="Anos de Experiência")
    exclusive_recipes = models.PositiveIntegerField(default=120, verbose_name="Receitas Exclusivas")
    class Meta:
        verbose_name = 'Estatística da Loja'
        verbose_name_plural = 'Estatísticas da Loja'

    def __str__(self):
        return "Estatísticas Iniciais"

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj

class Recipe(models.Model):
    title = models.CharField(max_length=200, verbose_name='Título da Receita')
    instructions = models.TextField(blank=True, verbose_name='Modo de Preparo')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return self.title

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    name = models.CharField(max_length=150, verbose_name='Ingrediente')
    quantity = models.CharField(max_length=50, verbose_name='Quantidade')
    
    def __str__(self): return f"{self.quantity} de {self.name}"
