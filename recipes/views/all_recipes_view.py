from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from recipes.models.recipe import Recipe
from recipes.helpers.recipe_query_helpers import get_search_query

from recipes.helpers.user_query_helpers import get_users_context
from recipes.helpers.recipe_query_helpers import get_recipes_context


@login_required
def all_recipes(request):
<<<<<<< HEAD
 """
 Display public recipes with search, filtering and pagination.
 """
 
=======
 """ Display public recipes with search, filtering and pagination. """
 base_queryset = Recipe.objects.filter(private=False)

>>>>>>> main
 search_query = get_search_query(request)
 tab = request.GET.get("tab", "recipes")

 base_context = {"search_query": search_query, "active_tab":tab}

 if tab == "recipes":
  context = get_recipes_context(request, search_query)
 else:
  context = get_users_context(request, search_query)

 return render(request, "recipes/all_recipes.html", {**base_context, **context})