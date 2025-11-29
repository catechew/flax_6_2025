from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render
from recipes.models.recipe import Recipe
from django.db.models import Q, F, Value, Count
from django.db.models.functions import Concat
from django.db.models import Avg

ITEMS_PER_PAGE = 25

# Filter options 
COURSE_OPTIONS = ['dessert', 'main', 'appetiser', 'breakfast', 'snack']
DIETARY_OPTIONS = ['vegetarian', 'vegan', 'halal', 'kosher', 'gluten-free', 'dairy-free']
CUISINE_OPTIONS = ['Japanese', 'Italian', 'Chinese', 'Asian', 'Persian', 'Jamaican', 'Western', 'British', 'Lebanese','Middle-Eastern']
OTHER_OPTIONS = ['high protein', 'low calorie', 'low carb', 'quick', 'budget']

# Dictionary mapping sort options to model fields
# Excludes complex sorts that need annotations (total_least etc)
SORT_OPTIONS = {
    'date_newest': '-publication_date',
    'date_oldest': 'publication_date',
    'prep_least': 'prep_time_hours',
    'prep_most': '-prep_time_hours',
    'cook_least': 'cook_time_hours',
    'cook_most': '-cook_time_hours',
    'title_az': 'title',
    'title_za': '-title',
}

def build_search_query(search_query, recipes):
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
    return recipes

def apply_tag_filters(recipes, course_filters, dietary_filters, cuisine_filters, other_filters):
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
    
    return recipes

def apply_sorting(recipes, sort_by):

    # Check if the field to sort by is in the SORT_OPTIONS dictionary
    if sort_by in SORT_OPTIONS:
        order_field = SORT_OPTIONS[sort_by]
        recipes = recipes.order_by(order_field)
        return recipes
    
    # If not, do more complex annotations
    if sort_by == 'total_least':
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
            save_count=Count('saved_by')
        )
        order_field = '-saved_by'
    elif sort_by == 'rating_highest':
        recipes = recipes.annotate(avg_rating=Avg('ratings__stars'))
        recipes = recipes.order_by(
            F('avg_rating').desc(nulls_last=True),
            '-publication_date'
        )
        order_field = None
    elif sort_by == 'title_az':
        order_field = 'title'
    elif sort_by == 'title_za':
        order_field = '-title'
    else:
        order_field = '-publication_date'

    if order_field:
        recipes = recipes.order_by(order_field)
    
    return recipes

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

    # Filter recipes by visibility
    recipes = recipes.filter(private=False)

    # Build search query
    recipes = build_search_query(search_query, recipes)

    # Apply tag filters
    recipes = apply_tag_filters(recipes, course_filters, dietary_filters, cuisine_filters, other_filters)

    # Get sort parameters
    sort_by = request.GET.get('sort', 'date_newest') # default to newest first

    # Apply sorting
    recipes = apply_sorting(recipes, sort_by)

    # Paginate results 
    paginator = Paginator(recipes, ITEMS_PER_PAGE)
    page_number = request.GET.get('page')
    page_object = paginator.get_page(page_number)
    
    total_count = recipes.count()

    # Calculate total active filters
    total_filters = len(course_filters) + len(dietary_filters) + len(cuisine_filters) + len(other_filters)
    
    context = {
        'user': current_user,
        'recipes': recipes,
        'page_object': page_object,
        'search_query': search_query,
        'total_count' : total_count,
        'course_options': COURSE_OPTIONS,
        'dietary_options': DIETARY_OPTIONS,
        'cuisine_options': CUISINE_OPTIONS,
        'other_options': OTHER_OPTIONS,
        'course_filters': course_filters,
        'dietary_filters': dietary_filters,
        'cuisine_filters': cuisine_filters,
        'other_filters': other_filters,
        'sort_by': sort_by,
        'total_filters': total_filters,
    }

    return render(request, 'all_recipes.html', context)
