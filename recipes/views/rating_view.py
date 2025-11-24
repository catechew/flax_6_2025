from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from recipes.models import Recipe
from recipes.models.rating import Rating
from django.contrib import messages


@login_required
def rate_recipe(request, recipe_id):
    """
    Handle submission of a user's star rating for a recipe.
    If user has already rated this recipe, rating is updated.
    """
    recipe = get_object_or_404(Recipe, id=recipe_id)

    # Prevent authors from rating their own recipes
    if recipe.author == request.user:
        messages.warning(request, "You cannot rate your own recipe.")
        return redirect("recipe_detail", recipe_id=recipe.id)

    if request.method == "POST":
        stars = int(request.POST.get("stars", 0))
        if 1 <= stars <= 5:
            Rating.objects.update_or_create(
                recipe=recipe,
                user=request.user,
                defaults={"stars": stars}
            )
            messages.success(request, "Your rating has been saved.")

    return redirect("recipe_detail", recipe_id=recipe.id)