from django.http import Http404
from django.shortcuts import render
from recipes.views.decorators import login_prohibited
from recipes.models.recipe import Recipe
from django.core.paginator import Paginator

ITEMS_PER_PAGE = 25


@login_prohibited
def home(request):
    """Display the application's start/home screen."""

    return render(request, 'home.html')

# use Paginator to list 25 recipes at a time, currently to the home page
def list_recipes(request):
    recipe_list = Recipe.objects.all()
    paginator = Paginator(recipe_list, ITEMS_PER_PAGE)
    # I think this code below is correct
    page_number = request.GET.get("page")
    page_object = paginator.get_page(page_number)
    context = {'page_object': page_object}
    return render(request, 'home.html', context) # context

# get one recipe. Am unsure if this function should be here!
def get_recipe(request, recipe_id):
    try:
        context = {'recipe': Recipe.objects.get(id=recipe_id)}
    except Recipe.DoesNotExist:
        raise Http404(f"Could not find book with primary key {recipe_id}") 
    else:
        return render(request, 'recipe.html', context)