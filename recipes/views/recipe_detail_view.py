from django.shortcuts import render
from recipes.handlers.recipe_detail_handler import RecipeDetailHandler


def recipe_detail(request, recipe_id):
    """ Display recipe details with optional cost estimation """
    handler = RecipeDetailHandler(request, recipe_id)
    context = handler.get_context()
    return render(request, 'recipes/recipe.html', context)