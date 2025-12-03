"""
Helper functions for searching, sorting and paginating users
"""

from django.db.models import Q, Count
from django.core.paginator import Paginator
from recipes.models.user import User
from recipes.models.recipe import Recipe
from recipes.helpers.recipe_query_helpers import apply_search

ITEMS_PER_PAGE = 25

def apply_user_search(users, search_query):
    """Apply search on user fields"""
    if not search_query:
        return users
    
    query = (
        Q(username__icontains=search_query)
        | Q(first_name__icontains=search_query)
        |Q(last_name__icontains=search_query)
    )

    return users.filter(query)

def paginate_users(users, request):
    """Return paginated user page."""
    paginator = Paginator(users, ITEMS_PER_PAGE)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)

def get_users_context(request, search_query):
    """Create context for users tab"""

    user_queryset = User.objects.all()
    filtered_users = apply_user_search(user_queryset, search_query)
    page_object = paginate_users(filtered_users, request)

    recipe_count = apply_search(Recipe.objects.filter(private=False), search_query).count()

    return {
        "users": page_object,
        "page_object": page_object,
        "user_count": page_object.paginator.count,
        "recipe_count": recipe_count
    }

