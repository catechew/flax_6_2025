from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from recipes.models.recipe import Recipe
from recipes.helpers.recipe_query_helpers import (
 get_search_query,
 get_filter_params,
 apply_search,
 apply_filters,
 apply_sort,
 paginate
)

@login_required
def all_recipes(request):
 """
 Display public recipes with search, filtering and pagination.
 """
 recipes = Recipe.objects.filter(private=False)

 search = get_search_query(request)
 filters = get_filter_params(request)
 sort_by = request.GET.get('sort', 'date_newest')

 recipes = apply_search(recipes, search)
 recipes = apply_filters(recipes, filters)
 recipes = apply_sort(recipes, sort_by)

 page_object = paginate(recipes, request)

 context = {
  'user': request.user,
  'recipes': recipes,
  'page_object': page_object,
  'search_query': search,
  'filters': filters,
  'sort_by': sort_by
 }

 return render(request, 'recipes/all_recipes.html', context)