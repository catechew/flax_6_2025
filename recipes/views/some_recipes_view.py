from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import render

from recipes.models.recipe import Recipe

ITEMS_PER_PAGE = 25

# Display specific recipes by their IDs
@login_required
def some_recipes(request):
    # Get IDs from URL query parameter (eg. '?ids=1,55,300')
    ids_param = request.GET.get('ids', '')
    
    # Take each ID from URL and convert to int
    id_strings = ids_param.split(',')
    recipe_ids = []
    for id in id_strings:
        if id: 
            recipe_ids.append(int(id))
    
    recipes = Recipe.objects.filter(id__in=recipe_ids)
    
    # Use Paginator to list 25 recipes at a time
    paginator = Paginator(recipes, ITEMS_PER_PAGE)
    page_object = paginator.get_page(request.GET.get('page'))
    
    context = {'recipes': recipes, 'page_object': page_object}
    return render(request, 'some_recipes.html', context)