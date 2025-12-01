"""
Helper functions for searching, filtering, sorting and paginating recipes.
"""

from django.db.models import Q, Avg, Count, F
from django.db.models.functions import Concat
from django.db.models import Value
from django.core.paginator import Paginator


ITEMS_PER_PAGE = 25

SORT_FIELD_MAP = {
    "date_newest": "-publication_date",
    "date_oldest": "publication_date",
    "title_az": "title",
    "title_za": "-title",
}


def get_search_query(request):
 """ Return cleaned search term from request. """
 return request.GET.get("q", "").strip()


def get_filter_params(request):
 """ Extract tag-based filters from request. """
 return {
  "course_filters": request.GET.getlist("course", []),
  "dietary_filters": request.GET.getlist("dietary", []),
  "cuisine_filters": request.GET.getlist("cuisine", []),
  "other_filters": request.GET.getlist("other", []),
 }


def apply_search(recipes, search_query):
 """ Apply free-text search on multiple recipe fields. """
 if not search_query:
  return recipes

 words = search_query.split()

 recipes = recipes.annotate(
  author_name=Concat(
   "author__first_name",
   Value(" "),
   "author__last_name",
  )
 )

 base_query = (
  Q(title__icontains=search_query)
  | Q(adjectives__icontains=search_query)
  | Q(steps__icontains=search_query)
  | Q(author_name__icontains=search_query)
 )

 ingredient_query = _build_ingredient_query(words)

 return recipes.filter(base_query | ingredient_query)


def _build_ingredient_query(words):
 """ Build AND-based ingredient filter. """
 query = Q()
 for word in words:
  query &= Q(ingredients__icontains=word)
 return query


def apply_filters(recipes, filters):
 """ Apply tag filters to queryset. """
 tag_map = {
  "course_filters": "course_tags",
  "dietary_filters": "dietary_tags",
  "cuisine_filters": "cuisine_tags",
  "other_filters": "other_tags",
 }

 for key, field in tag_map.items():
  values = filters.get(key)
  if values:
   recipes = recipes.filter(_build_tag_query(field, values))

 return recipes


def _build_tag_query(field, values):
 """ Build OR-based tag query. """
 query = Q()
 for value in values:
  query |= Q(**{f"{field}__icontains": value})
 return query


def apply_sort(recipes, sort_by):
    """ Apply sorting based on selected option. """

    # Simple DB field sorts
    if sort_by in SORT_FIELD_MAP:
        return recipes.order_by(SORT_FIELD_MAP[sort_by])

    # Total Time (prep + cook)
    if sort_by in ["total_least", "total_most"]:
        recipes = recipes.annotate(
            total_minutes=(
                (F("prep_time_hours") * 60 + F("prep_time_minutes")) +
                (F("cook_time_hours") * 60 + F("cook_time_minutes"))
            )
        )
        return recipes.order_by(
            "total_minutes" if sort_by == "total_least" else "-total_minutes"
        )
    
    # Prep Time 
    if sort_by in ["prep_least", "prep_most"]:
      recipes = recipes.annotate(
        prep_minutes = F("prep_time_hours") * 60 + F("prep_time_minutes")
      )
      return recipes.order_by(
        "prep_minutes" if sort_by == "prep_least" else "-prep_minutes"
      )
    
    # Cook Time
    if sort_by in ["cook_least", "cook_most"]:
      recipes = recipes.annotate(
        cook_minutes = F("cook_time_hours") * 60 + F("cook_time_minutes")
      )
      return recipes.order_by(
        "cook_minutes" if sort_by == "cook_least" else "-cook_minutes"
      )

    # Most saved
    if sort_by == "most_saved":
        return recipes.annotate(
            save_count=Count("saved_by")
        ).order_by("-save_count", "-publication_date")

    # Highest rated
    if sort_by == "rating_highest":
        return recipes.annotate(
            avg_rating=Avg("ratings__stars")
        ).order_by(
            F("avg_rating").desc(nulls_last=True),
            "-publication_date"
        )

    # Fallback
    return recipes.order_by("-publication_date")


def paginate(recipes, request):
 """ Return paginated recipe page. """
 paginator = Paginator(recipes, ITEMS_PER_PAGE)
 page_number = request.GET.get("page")
 return paginator.get_page(page_number)