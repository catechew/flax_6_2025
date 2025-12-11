from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render
from recipes.models.recipe import Recipe

ITEMS_PER_PAGE = 25


@login_required
def some_recipes(request):
    """Display a subset of recipes specified by ID query parameters."""
    ids_param = request.GET.get("ids", "")
    recipe_ids = _parse_recipe_ids(ids_param)
    recipes = Recipe.objects.visible().filter(id__in=recipe_ids)
    page_object = _paginate_recipes(recipes, request)
    context = {"recipes": recipes, "page_object": page_object}
    return render(request, "ai/some_recipes.html", context)


def _parse_recipe_ids(ids_param):
    """Parse comma-separated recipe IDs, skipping invalid values."""
    parsed_ids = map(_try_parse_int, ids_param.split(","))
    return [id for id in parsed_ids if id is not None]


def _try_parse_int(value):
    """Try to parse string as int, return None if invalid."""
    try:
        return int(value)
    except ValueError:
        return None


def _paginate_recipes(recipes, request):
    """Paginate recipe queryset."""
    paginator = Paginator(recipes, ITEMS_PER_PAGE)
    return paginator.get_page(request.GET.get("page"))
