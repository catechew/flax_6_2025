from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from recipes.models.recipe import Recipe
from django.core.paginator import Paginator
from django.db.models import Q

ITEMS_PER_PAGE = 25

# use Paginator to list 25 recipes at a time
@login_required
def list_recipes(request):
    """
    Display all recipes.
    """
    recipe_list = Recipe.objects.all()
    paginator = Paginator(recipe_list, ITEMS_PER_PAGE)
    # I think this code below is correct
    page_number = request.GET.get("page")
    page_object = paginator.get_page(page_number)
    context = {'page_object': page_object}
    return render(request, 'home.html', context) # context

# get all recipes
def all_recipes(request):
    current_user = request.user

    # get search query from navbar
    search_query = request.GET.get('q', '').strip()

    # start with all recipes
    recipes = Recipe.objects.all()

    # if there's a search query, filter recipes
    if search_query:
        recipes = recipes.filter(
            Q(title__icontains=search_query) |
            Q(adjectives__icontains=search_query)
        )
    
    context = {
        'user': current_user,
        'recipes': recipes,
        'search_query': search_query,
    }

    return render(request, 'all_recipes.html', context)
