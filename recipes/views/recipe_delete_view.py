from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from recipes.models.recipe import Recipe


@login_required
def recipe_delete(request, recipe_id):
    """Delete a recipe (author or admin only)."""
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if not _can_delete_recipe(request.user, recipe):
        return HttpResponseForbidden("You don't have permission to delete this recipe.")

    if request.method == "POST":
        recipe.delete()
        return HttpResponseRedirect(reverse("all_recipes"))

    return render(request, "recipes/delete_recipe.html", {"recipe": recipe})


def _can_delete_recipe(user, recipe):
    """Check if user can delete recipe (author or admin)."""
    return recipe.author == user or user.is_staff
