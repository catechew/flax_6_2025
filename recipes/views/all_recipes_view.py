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
    # Get all recipes
    current_user = request.user

    # Get search query from navbar
    search_query = request.GET.get('q', '')
    if search_query is not None:
        search_query = search_query.strip()
    else:
        search_query = ''

    # Get filter parameters
    course_filter = request.GET.get('course', '')
    dietary_filter = request.GET.get('dietary', '')
    cuisine_filter = request.GET.get('cuisine', '')
    other_filter = request.GET.get('other', '')

    # Start with all recipes
    recipes = Recipe.objects.all()

    # If there's a search query, filter recipes
    if search_query:
        recipes = recipes.filter(
            Q(title__icontains=search_query) |
            Q(adjectives__icontains=search_query) |
            Q(ingredients__icontains=search_query) |
            Q(steps__icontains=search_query) |
            Q(adjectives__icontains=search_query) 
        )

    # Apply tag filters
    if course_filter:
        recipes = recipes.filter(course_tags__icontains=course_filter)

    if dietary_filter:
        recipes = recipes.filter(dietary_tags__icontains=dietary_filter)

    if cuisine_filter:
        recipes = recipes.filter(cuisine_tags__icontains=cuisine_filter)

    if other_filter:
        recipes = recipes.filter(other_tags__icontains=other_filter)

    # Ensure ordering (newest first)
    recipes = recipes.order_by('-publication_date')

    # Filter options
    course_options = ['dessert', 'main', 'appetiser', 'breakfast', 'snack']
    dietary_options = ['vegetarian', 'vegan', 'halal', 'kosher', 'gluten-free', 'dairy-free']
    cuisine_options = ['Japanese', 'Italian', 'Chinese', 'Asian', 'Persian', 'Jamaican', 'Western', 'British', 'Lebanese','Middle-Eastern']
    other_options = ['high protein', 'low calorie', 'low carb', 'quick', 'budget']

    # Paginate results 
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
        'course_options': course_options,
        'dietary_options': dietary_options,
        'cuisine_options': cuisine_options,
        'other_options': other_options,
        'course_filter': course_filter,
        'dietary_filter': dietary_filter,
        'cuisine_filter': cuisine_filter,
        'other_filter': other_filter,
    }

    return render(request, 'all_recipes.html', context)
