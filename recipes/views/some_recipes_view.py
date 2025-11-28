from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import render

from recipes.models.recipe import Recipe

ITEMS_PER_PAGE = 25

# Display specific recipes by their IDs
@login_required
<<<<<<< HEAD
def some_recipes(request):
    # Get IDs from URL query parameter (eg. '?ids=1,55,300')
    ids_param = request.GET.get('ids', '')
    recipe_ids = [int(id) for id in ids_param.split(',') if id]
    
    recipes = Recipe.objects.filter(id__in=recipe_ids)
    
=======
def some_recipes(request, recipe_ids):
    recipes = Recipe.objects.filter(id__in=recipe_ids)
>>>>>>> 200a1378c56f9ae5ef5a8f6c07dc28a3a7a0626b
    # Use Paginator to list 25 recipes at a time
    paginator = Paginator(recipes, ITEMS_PER_PAGE)
    page_object = paginator.get_page(request.GET.get('page'))
    
    context = {'recipes': recipes, 'page_object': page_object}
    return render(request, 'some_recipes.html', context)