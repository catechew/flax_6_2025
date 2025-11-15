from recipes.models.recipe import Recipe
from django.http import Http404
from django.shortcuts import render

# get one recipe. Am unsure if this function should be here!
def get_recipe(request, recipe_id):
    try:
        context = {'recipe': Recipe.objects.get(id=recipe_id)}
    except Recipe.DoesNotExist:
        raise Http404(f"Could not find recipe with primary key {recipe_id}") 
    else:
        return render(request, 'recipe.html', context)