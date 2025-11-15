from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render
from recipes.models.recipe import Recipe

ITEMS_PER_PAGE = 25

# Use Paginator to list 25 recipes at a time
@login_required
def all_recipes(request):
    """
    Display all recipes.
    """
    recipe_list = Recipe.objects.all()
    paginator = Paginator(recipe_list, ITEMS_PER_PAGE)

    page_number = request.GET.get("page")
    page_object = paginator.get_page(page_number)

    context = {
        "page_object": page_object,
        "recipes": page_object.object_list
    }

    return render(request, 'all_recipes.html', context) # context
