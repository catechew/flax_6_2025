"""
Helper functions for searching, sorting and paginating users
"""

from django.db.models import Q, Count
from django.core.paginator import Paginator

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
