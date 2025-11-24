from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render
from recipes.models.recipe import Recipe
from django.db.models import Q, F, Value, Count
from django.db.models.functions import Concat

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
        # Split search words into individual words
        search_words = search_query.split()
        recipes = recipes.annotate(
            full_name=Concat('author__first_name', Value(' '), 'author__last_name')
        )
        
        # if multiple words, check if ALL appear in ingredients
        if len(search_words) > 1:
            # filter to check if all words are in ingredients
            ingredients_filter = Q()
            for word in search_words:
                ingredients_filter &= Q(ingredients__icontains=word)

            # Apply QR logic for other fields and logic for multi-word ingredients
            recipes = recipes.filter(
                Q(title__icontains=search_query) |
                Q(adjectives__icontains=search_query) |
                ingredients_filter |
                Q(steps__icontains=search_query) |
                Q(author__username__icontains=search_query) |
                Q(author__first_name__icontains=search_query) |
                Q(author__last_name__icontains=search_query) |
                Q(full_name__icontains=search_query) 
            )
        else:
            # Single word search
            recipes = recipes.filter(
                Q(title__icontains=search_query) |
                Q(adjectives__icontains=search_query) |
                Q(ingredients__icontains=search_query) |
                Q(steps__icontains=search_query) |
                Q(author__username__icontains=search_query) |
                Q(author__first_name__icontains=search_query) |
                Q(author__last_name__icontains=search_query) |
                Q(full_name__icontains=search_query) 
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

    # Get sort parameters
    sort_by = request.GET.get('sort', 'date_newest') # default to newest first

    # Apply sorting
    if sort_by == 'date_newest':
        order_field = '-publication_date'
    elif sort_by == 'date_oldest':
        order_field = 'publication_date'
    elif sort_by == 'prep_least':
        order_field = 'prep_time_hours'
    elif sort_by == 'prep_most':
        order_field = '-prep_time_hours'
    elif sort_by == 'cook_least':
        order_field = 'cook_time_hours'
    elif sort_by == 'cook_most':
        order_field = '-cook_time_hours'
    elif sort_by == 'total_least':
      recipes = recipes.annotate(
          total_minutes=(F('prep_time_hours') + F('cook_time_hours')) * 60 +
                        (F('prep_time_minutes') + F('cook_time_minutes'))
      )
      order_field = 'total_minutes'
    elif sort_by == 'total_most':
        recipes = recipes.annotate(
            total_minutes=(F('prep_time_hours') + F('cook_time_hours')) * 60 +
                            (F('prep_time_minutes') + F('cook_time_minutes'))
        )
        order_field = '-total_minutes'
    elif sort_by == 'most_saves':
        recipes = recipes.annotate(
            save_count=models.Count('saved_by')
        )
        order_field = '-saved_by'
    elif sort_by == 'title_az':
        order_field = 'title'
    elif sort_by == 'title_za':
        order_field = '-title'
    else:
        order_field = '-publication_date'

    recipes = recipes.order_by(order_field)

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
        'sort_by': sort_by,
    }

    return render(request, 'all_recipes.html', context)
