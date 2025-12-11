from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from recipes.handlers.recipe_form_handler import RecipeFormHandler


@login_required
def recipe_tags_view(request, recipe_id=None):
    """If recipe_id is None: create. Else: update."""
    handler = RecipeFormHandler(request, recipe_id)

    if "form_data" not in handler.session_data:
        return handler.show_missing_form_data_warning()

    if request.method != "POST":
        context = handler.get_tags_context()
        return render(request, "recipes/recipe_tags_form.html", context)
    response = handler.handle_tags_post()

    if response:
        return response
    context = handler.get_tags_context()
    return render(request, "recipes/recipe_tags_form.html", context)
