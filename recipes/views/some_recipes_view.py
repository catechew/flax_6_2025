from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render

from recipes.models.recipe import Recipe


ITEMS_PER_PAGE = 25


@login_required
def some_recipes(request):
    """
    Display a subset of recipes specified by ID query parameters.
    """

    ids_param = request.GET.get('ids', '')

    recipe_ids = []
    for value in ids_param.split(','):
        try:
            recipe_ids.append(int(value))
        except ValueError:
            continue

    recipes = Recipe.objects.visible().filter(id__in=recipe_ids)

    paginator = Paginator(recipes, ITEMS_PER_PAGE)
    page_object = paginator.get_page(request.GET.get('page'))
    
    context = {'recipes': recipes, 'page_object': page_object}
    return render(request, 'ai/some_recipes.html', context)