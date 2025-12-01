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
    "prep_least": "prep_time_hours",
    "prep_most": "-prep_time_hours",
    "cook_least": "cook_time_hours",
    "cook_most": "-cook_time_hours",
}


def get_search_query(request):
 """ Return cleaned search term from request. """
 return request.GET.get("q", "").strip()


def get_filter_params(request):
 """ Extract tag-based filters from request. """
 return {
  "course": request.GET.getlist("course", []),
  "dietary": request.GET.getlist("dietary", []),
  "cuisine": request.GET.getlist("cuisine", []),
  "other": request.GET.getlist("other", []),
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
  "course": "course_tags",
  "dietary": "dietary_tags",
  "cuisine": "cuisine_tags",
  "other": "other_tags",
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
 """ Apply ordering based on sort parameter. """
 if sort_by == "rating_highest":
  return recipes.annotate(
   avg_rating=Avg("ratings__stars")
  ).order_by("-avg_rating", "-publication_date")

 return recipes.order_by("-publication_date")


def paginate(recipes, request):
 """ Return paginated recipe page. """
 paginator = Paginator(recipes, ITEMS_PER_PAGE)
 page_number = request.GET.get("page")
 return paginator.get_page(page_number)