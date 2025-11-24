from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from recipes.models import Recipe
from recipes.models.rating import Rating


@login_required
def rate_recipe(request, recipe_id):
    """
    Handles submission of a user's star rating for a recipe.
    If the user has already rated this recipe, the rating is updated.
    """
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if request.method == "POST":
        stars = int(request.POST.get("stars", 0))
        if 1 <= stars <= 5:
            Rating.objects.update_or_create(
                recipe=recipe,
                user=request.user,
                defaults={"stars": stars}
            )

    return redirect("recipe_detail", recipe_id=recipe.id)