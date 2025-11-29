from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from recipes.models import Recipe
from recipes.models.flag import Flag
from django.contrib import messages


@login_required
def flag_recipe(request, recipe_id):
    """Allow users to flag/report a recipe."""
    recipe = get_object_or_404(Recipe, id=recipe_id)

    # Check if user already flagged this recipe
    existing_flag = Flag.objects.filter(recipe=recipe, user=request.user).first()

    if existing_flag:
        messages.warning(request, "You've already flagged this recipe.")
    else:
        # Create flag
        Flag.objects.create(
            recipe=recipe,
            user=request.user,
        )
        messages.success(request, "Recipe has been flagged for review. Thank you for helping keep Recipify safe!")

    # Redirect back to recipe detail
    return redirect('recipe_detail', recipe_id=recipe.id)