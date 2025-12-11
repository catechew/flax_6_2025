from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def save_ai_recipe_view(request):
    """Transfer AI recipe to create form."""
    ai_recipe = request.session.get("last_ai_recipe")
    if not ai_recipe:
        return handle_missing_ai_recipe(request)
    store_ai_recipe_for_form(request, ai_recipe)
    show_ai_loaded_message(request)
    return redirect("create_recipe")


def handle_missing_ai_recipe(request):
    """Handle case where no AI recipe exists."""
    messages.error(request, "No AI recipe found. Please generate a recipe first.")
    return redirect("ai_recipe_generator")


def store_ai_recipe_for_form(request, ai_recipe):
    """Store AI recipe in session for form prefill."""
    request.session["ai_recipe_prefill"] = ai_recipe
    request.session["from_ai_save_button"] = True
    request.session.pop("last_ai_recipe", None)


def show_ai_loaded_message(request):
    """Show success message for AI recipe load."""
    messages.info(
        request, "Recipe loaded! Review, customise it as you wish, then save."
    )
