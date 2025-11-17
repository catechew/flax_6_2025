from recipes.models.recipe import Recipe
from django.http import Http404
from django.shortcuts import render

def recipe_detail(request, recipe_id):
    try:
        recipe = Recipe.objects.get(id=recipe_id)
    except Recipe.DoesNotExist:
        raise Http404(f"Could not find recipe with primary key {recipe_id}") 
   
    return render(request, 'recipe.html', {'recipe': recipe})