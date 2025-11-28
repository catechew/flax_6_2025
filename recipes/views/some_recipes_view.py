from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import render

from recipes.models.recipe import Recipe

ITEMS_PER_PAGE = 25

# Display specific recipes by their IDs
@login_required
def some_recipes(request, recipe_ids):
    recipes = Recipe.objects.filter(id__in=recipe_ids)
    # Use Paginator to list 25 recipes at a time
    paginator = Paginator(recipes, ITEMS_PER_PAGE)
    page_object = paginator.get_page(request.GET.get('page'))
    
    context = {'recipes': recipes, 'page_object': page_object}
    return render(request, 'some_recipes.html', context)