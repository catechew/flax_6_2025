from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from recipes.models import Recipe
from recipes.models.flag import Flag


@login_required
def flag_recipe(request, recipe_id):
    """Allow users to flag/report a recipe."""
    recipe = get_object_or_404(Recipe, id=recipe_id)
    existing_flag = Flag.objects.filter(recipe=recipe, user=request.user).first()

    if existing_flag:
        messages.warning(request, "You've already flagged this recipe.")
    else:
        Flag.objects.create(
            recipe=recipe,
            user=request.user,
        )
        messages.success(
            request,
            "Recipe has been flagged for review. Thank you for helping keep Recipify safe!",
        )
    return redirect("recipe_detail", recipe_id=recipe.id)


@login_required
def unflag_recipe(request, recipe_id):
    """Allow users to unflag/unreport a recipe."""
    recipe = get_object_or_404(Recipe, id=recipe_id)
    deleted_count, _ = Flag.objects.filter(recipe=recipe, user=request.user).delete()

    if deleted_count > 0:
        messages.success(request, "Flag removed.")
    else:
        messages.warning(request, "You haven't flagged this recipe.")
    return redirect("recipe_detail", recipe_id=recipe.id)
