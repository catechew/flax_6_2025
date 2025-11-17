from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render
from recipes.models.recipe import Recipe
from django.db.models import Q

ITEMS_PER_PAGE = 25

# Use Paginator to list 25 recipes at a time
@login_required
def all_recipes(request):
    """
    Display all recipes.
    """
    # get all recipes
    current_user = request.user

    # get search query from navbar
    search_query = request.GET.get('q', '')
    if search_query is not None:
        search_query = search_query.strip()
    else:
        search_query = ''

    # start with all recipes
    recipes = Recipe.objects.all()

    # if there's a search query, filter recipes
    if search_query:
        recipes = recipes.filter(
            Q(title__icontains=search_query) |
            Q(adjectives__icontains=search_query)
        )

    # ensure ordering (newest first)
    recipes = recipes.order_by('-publication_date')

    # paginate results 
    paginator = Paginator(recipes, ITEMS_PER_PAGE)
    page_number = request.GET.get('page')
    page_object = paginator.get_page(page_number)
    
    total_count = recipes.count()
    
    context = {
        'user': current_user,
        'recipes': recipes,
        'page_object': page_object,
        'search_query': search_query,
        'total_count' : total_count,
    }

    return render(request, 'all_recipes.html', context)
