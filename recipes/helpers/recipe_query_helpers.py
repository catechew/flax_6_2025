from django.db.models import Q, Avg, Count, F
from django.db.models.functions import Concat
from django.db.models import Value
from django.core.paginator import Paginator
from recipes.models.recipe import Recipe
from recipes.models.user import User
from recipes.helpers.user_query_helpers import apply_user_search
from recipes.helpers.recipe_filter_options import (
    COURSE_OPTIONS,
    DIETARY_OPTIONS,
    CUISINE_OPTIONS,
    OTHER_OPTIONS,
    SORT_OPTIONS,
)

"""
Helper functions for searching, filtering, sorting and paginating recipes.
"""

ITEMS_PER_PAGE = 25

SORT_FIELD_MAP = {
    "date_newest": "-publication_date",
    "date_oldest": "publication_date",
    "title_az": "title",
    "title_za": "-title",
}


def get_search_query(request):
    """Return cleaned search term from request."""
    return request.GET.get("q", "").strip()


def get_filter_params(request):
    """Extract tag-based filters from request."""
    return {
        "course_filters": request.GET.getlist("course", []),
        "dietary_filters": request.GET.getlist("dietary", []),
        "cuisine_filters": request.GET.getlist("cuisine", []),
        "other_filters": request.GET.getlist("other", []),
    }


def apply_search(recipes, search_query):
    """Apply free-text search on multiple recipe fields."""
    if not search_query:
        return recipes
    recipes = _annotate_author_name(recipes)
    base_query = _build_base_search_query(search_query)
    ingredient_query = _build_ingredient_query(search_query.split())
    return recipes.filter(base_query | ingredient_query)


def _annotate_author_name(recipes):
    """Add author full name annotation to queryset."""
    return recipes.annotate(
        author_name=Concat(
            "author__first_name",
            Value(" "),
            "author__last_name",
        )
    )


def _build_base_search_query(search_query):
    """Build search query for title, steps, author fields."""
    return (
        Q(title__icontains=search_query)
        | Q(adjectives__icontains=search_query)
        | Q(steps__icontains=search_query)
        | Q(author_name__icontains=search_query)
        | Q(author__username__icontains=search_query)
    )


def _build_ingredient_query(words):
    """Build AND-based ingredient filter."""
    query = Q()
    for word in words:
        query &= Q(ingredients__icontains=word)
    return query


def apply_filters(recipes, filters):
    """Apply tag filters to queryset."""
    tag_map = {
        "course_filters": "course_tags",
        "dietary_filters": "dietary_tags",
        "cuisine_filters": "cuisine_tags",
        "other_filters": "other_tags",
    }
    for key, field in tag_map.items():
        recipes = _apply_tag_filter(recipes, filters, key, field)
    return recipes


def _apply_tag_filter(recipes, filters, key, field):
    """Apply a single tag filter if values exist."""
    values = filters.get(key)
    if not values:
        return recipes
    return recipes.filter(_build_tag_query(field, values))


def _build_tag_query(field, values):
    """Build OR-based tag query."""
    query = Q()
    for value in values:
        query |= Q(**{f"{field}__icontains": value})
    return query


def apply_sort(recipes, sort_by):
    """Apply sorting based on selected option."""
    if sort_by in SORT_FIELD_MAP:
        return recipes.order_by(SORT_FIELD_MAP[sort_by])
    sort_map = _get_sort_function_map()
    sort_func = sort_map.get(sort_by, _default_sort)
    return sort_func(recipes)


def _get_sort_function_map():
    """Get mapping of sort options to functions."""
    return {
        "total_least": lambda r: _sort_by_total_time(r, "total_least"),
        "total_most": lambda r: _sort_by_total_time(r, "total_most"),
        "prep_least": lambda r: _sort_by_prep_time(r, "prep_least"),
        "prep_most": lambda r: _sort_by_prep_time(r, "prep_most"),
        "cook_least": lambda r: _sort_by_cook_time(r, "cook_least"),
        "cook_most": lambda r: _sort_by_cook_time(r, "cook_most"),
        "most_saved": _sort_by_saves,
        "rating_highest": _sort_by_rating,
    }


def _default_sort(recipes):
    """Apply default date-based sorting."""
    return recipes.order_by("-publication_date")


def _sort_by_total_time(recipes, sort_by):
    """Sort by total time (prep + cook)."""
    recipes = recipes.annotate(
        total_minutes=(
            (F("prep_time_hours") * 60 + F("prep_time_minutes"))
            + (F("cook_time_hours") * 60 + F("cook_time_minutes"))
        )
    )
    order = "total_minutes" if sort_by == "total_least" else "-total_minutes"
    return recipes.order_by(order)


def _sort_by_prep_time(recipes, sort_by):
    """Sort by preparation time."""
    recipes = recipes.annotate(
        prep_minutes=F("prep_time_hours") * 60 + F("prep_time_minutes")
    )
    order = "prep_minutes" if sort_by == "prep_least" else "-prep_minutes"
    return recipes.order_by(order)


def _sort_by_cook_time(recipes, sort_by):
    """Sort by cooking time."""
    recipes = recipes.annotate(
        cook_minutes=F("cook_time_hours") * 60 + F("cook_time_minutes")
    )
    order = "cook_minutes" if sort_by == "cook_least" else "-cook_minutes"
    return recipes.order_by(order)


def _sort_by_saves(recipes):
    """Sort by number of saves."""
    return recipes.annotate(save_count=Count("saved_by")).order_by(
        "-save_count", "-publication_date"
    )


def _sort_by_rating(recipes):
    """Sort by average rating."""
    return recipes.annotate(avg_rating=Avg("ratings__stars")).order_by(
        F("avg_rating").desc(nulls_last=True), "-publication_date"
    )


def paginate(recipes, request):
    """Return paginated recipe page."""
    paginator = Paginator(recipes, ITEMS_PER_PAGE)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def build_filter_params_string(filters, sort_by):
    """Build URL parameter string for filters."""
    filter_keys = [
        ("course_filters", "course"),
        ("dietary_filters", "dietary"),
        ("cuisine_filters", "cuisine"),
        ("other_filters", "other"),
    ]
    params = []
    for filter_key, param_name in filter_keys:
        params.extend(_build_param_list(filters, filter_key, param_name))
    params.append(f"&sort={sort_by}")
    return "".join(params)


def _build_param_list(filters, filter_key, param_name):
    """Build parameter list for a specific filter type."""
    return [f"&{param_name}={value}" for value in filters.get(filter_key, [])]


def get_recipes_context(request, search_query):
    """Create context for recipes tab."""
    base_queryset = Recipe.objects.visible()
    filter_params = get_filter_params(request)
    sort_by = request.GET.get("sort", "date_newest")
    filtered_recipes = _apply_all_filters(
        base_queryset, search_query, filter_params, sort_by
    )
    page_object = paginate(filtered_recipes, request)
    user_count = apply_user_search(User.objects.all(), search_query).count()

    return _build_context_dict(
        page_object, search_query, filter_params, sort_by, user_count
    )


def _apply_all_filters(recipes, search_query, filter_params, sort_by):
    """Apply search, filters, and sorting to recipes."""
    recipes = apply_search(recipes, search_query)
    recipes = apply_filters(recipes, filter_params)
    recipes = apply_sort(recipes, sort_by)
    return recipes


def _build_context_dict(page_object, search_query, filter_params, sort_by, user_count):
    return {"recipes": page_object,
            "page_object": page_object,
            "search_query": search_query,
            "filters": filter_params,
            "total_filters": sum(len(v) for v in filter_params.values()),
            "sort_by": sort_by,
            "course_options": COURSE_OPTIONS,
            "dietary_options": DIETARY_OPTIONS,
            "cuisine_options": CUISINE_OPTIONS,
            "other_options": OTHER_OPTIONS,
            "sort_options": SORT_OPTIONS,
            "recipe_count": page_object.paginator.count,
            "user_count": user_count,
            "pagination_extra_params": build_filter_params_string(filter_params, sort_by), }
