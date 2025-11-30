"""
Helper functions for searching, filtering, sorting, and paginating recipes.
"""

from django.core.paginator import Paginator
from django.db.models import Q, F, Value, Avg
from django.db.models.functions import Concat

ITEMS_PER_PAGE = 25


def get_search_query(request):
 """ Return cleaned search query string from request. """
 search = request.GET.get("q", "")
 return search.strip()

def get_filter_params(request):
 """ Extract selected tag filters from request parameters. """
 return {
  "course": request.GET.getlist("course", []),
  "dietary": request.GET.getlist("dietary", []),
  "cuisine": request.GET.getlist("cuisine", []),
  "other": request.GET.getlist("other", []),
 }

def apply_search(recipes, search_query):
 """ Apply keyword-based search across recipe fields. """
 if not search_query:
  return recipes

 words = search_query.split()

 recipes = recipes.annotate(
  full_name=Concat(
   "author__first_name",
   Value(" "),
   "author__last_name",
  )
 )

 filters = (
  Q(title__icontains=search_query)
  | Q(adjectives__icontains=search_query)
  | Q(steps__icontains=search_query)
  | Q(full_name__icontains=search_query)
 )

 if len(words) > 1:
  ingredients_q = Q()
  for word in words:
   ingredients_q &= Q(ingredients__icontains=word)
  filters |= ingredients_q
 else:
  filters |= Q(ingredients__icontains=search_query)

 return recipes.filter(filters)

def apply_filters(recipes, filters):
 """ Apply tag-based filtering using selected categories. """
 tag_map = {
  "course": "course_tags",
  "dietary": "dietary_tags",
  "cuisine": "cuisine_tags",
  "other": "other_tags",
 }

 for key, field in tag_map.items():
  selected = filters.get(key)
  if selected:
   q = Q()
   for value in selected:
    q |= Q(**{f"{field}__icontains": value})
   recipes = recipes.filter(q)

 return recipes

def apply_sort(recipes, sort_by):
 """ Sort recipes by selected criterion. """
 if sort_by == "rating_highest":
  return recipes.annotate(
   avg_rating=Avg("ratings__stars")
  ).order_by(
   F("avg_rating").desc(nulls_last=True)
  )

 return recipes.order_by("-publication_date")

def paginate(recipes, request):
 """ Paginate recipes using request page parameter. """
 paginator = Paginator(recipes, ITEMS_PER_PAGE)
 page_number = request.GET.get("page")
 return paginator.get_page(page_number)