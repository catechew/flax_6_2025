from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from recipes.models.recipe import Recipe
from recipes.helpers.recipe_query_helpers import (
 get_search_query,
 get_filter_params,
 apply_search,
 apply_filters,
 apply_sort,
 paginate,
)
from recipes.helpers.recipe_filter_options import (
 COURSE_OPTIONS,
 DIETARY_OPTIONS,
 CUISINE_OPTIONS,
 OTHER_OPTIONS,
 SORT_OPTIONS,
)


@login_required
def all_recipes(request):
 """
 Display public recipes with search, filtering and pagination.
 """
 base_queryset = Recipe.objects.filter(private=False)

 search_query = get_search_query(request)
 filter_params = get_filter_params(request)
 sort_by = request.GET.get("sort", "date_newest")

 filtered_recipes = apply_search(base_queryset, search_query)
 filtered_recipes = apply_filters(filtered_recipes, filter_params)
 filtered_recipes = apply_sort(filtered_recipes, sort_by)

 page_object = paginate(filtered_recipes, request)

 total_filters = sum(len(v) for v in filter_params.values())

 context = {
  "recipes": page_object,
  "page_object": page_object,
  "search_query": search_query,
  "filters": filter_params,
#   "course_filters":filter_params.get("course", []),
#   "dietary_filters": filter_params.get("dietary", []),
#   "cuisine_filters": filter_params.get("cuisine", []),
#   "other_filters": filter_params.get("other", []),
  "sort_by": sort_by,
  "total_filters": total_filters,
  "course_options": COURSE_OPTIONS,
  "dietary_options": DIETARY_OPTIONS,
  "cuisine_options": CUISINE_OPTIONS,
  "other_options": OTHER_OPTIONS,
  "sort_options": SORT_OPTIONS,
 }

 return render(request, "recipes/all_recipes.html", context)