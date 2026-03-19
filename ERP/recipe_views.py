from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import Recipe, RecipeIngredient

@staff_member_required
def create_recipe(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        instructions = request.POST.get('instructions')
        if title:
            recipe = Recipe.objects.create(title=title, instructions=instructions)
            
            names = request.POST.getlist('ingredient_name[]')
            qtys = request.POST.getlist('ingredient_qty[]')
            
            for name, qty in zip(names, qtys):
                if name.strip() and qty.strip():
                    RecipeIngredient.objects.create(recipe=recipe, name=name.strip(), quantity=qty.strip())
            
            messages.success(request, 'Receita criada com sucesso!')
            return redirect('ERP:admin')
    
    return render(request, 'ERP/recipe_form.html', {'action': 'Criar'})

@staff_member_required
def edit_recipe(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == 'POST':
        recipe.title = request.POST.get('title', recipe.title)
        recipe.instructions = request.POST.get('instructions', recipe.instructions)
        recipe.save()
        recipe.ingredients.all().delete()
        names = request.POST.getlist('ingredient_name[]')
        qtys = request.POST.getlist('ingredient_qty[]')
        
        for name, qty in zip(names, qtys):
            if name.strip() and qty.strip():
                RecipeIngredient.objects.create(recipe=recipe, name=name.strip(), quantity=qty.strip())
                
        messages.success(request, 'Receita atualizada!')
        return redirect('ERP:admin')
        
    return render(request, 'ERP/recipe_form.html', {'action': 'Editar', 'recipe': recipe})

@staff_member_required
def delete_recipe(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == 'POST':
        recipe.delete()
        messages.success(request, 'Receita excluída!')
        return redirect('ERP:admin')
    return render(request, 'ERP/recipe_confirm_delete.html', {'object': recipe, 'type': 'Receita', 'cancel_url': 'ERP:admin'})
