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
    course_filters = request.GET.getlist('course', '')
    dietary_filters = request.GET.getlist('dietary', '')
    cuisine_filters = request.GET.getlist('cuisine', '')
    other_filters = request.GET.getlist('other', '')

    # Start with all recipes
    recipes = Recipe.objects.all()

    # If there's a search query, filter recipes
    if search_query:
        recipes = recipes.filter(
            Q(title__icontains=search_query) |
            Q(adjectives__icontains=search_query) |
            Q(ingredients__icontains=search_query) |
            Q(steps__icontains=search_query) 
        )

    # Apply tag filters
    if course_filters:
        course_q = Q()
        for course in course_filters:
            course_q |= Q(course_tags__icontains=course)
        recipes = recipes.filter(course_q)

    if dietary_filters:
        dietary_q = Q()
        for dietary in dietary_filters:
            dietary_q |= Q(dietary_tags__icontains=dietary)
        recipes = recipes.filter(dietary_q)

    if cuisine_filters:
        cuisine_q = Q()
        for cuisine in cuisine_filters:
            cuisine_q |= Q(cuisine_tags__icontains=cuisine)
        recipes = recipes.filter(cuisine_q)

    if other_filters:
        other_q = Q()
        for other in other_filters:
            other_q |= Q(other_tags__icontains=other)
        recipes = recipes.filter(other_q)

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
        'course_filters': course_filters,
        'dietary_filters': dietary_filters,
        'cuisine_filters': cuisine_filters,
        'other_filters': other_filters,
    }

    return render(request, 'all_recipes.html', context)
