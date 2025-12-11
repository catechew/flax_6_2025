from django.contrib import messages
from django.shortcuts import redirect


def redirect_to_form(handler):
    if handler.is_create_mode:
        return redirect("create_recipe")
    return redirect("update_recipe", recipe_id=handler.recipe_id)


def redirect_to_tags(handler):
    """Redirect to step 2 (tags) based on mode."""
    if handler.is_create_mode:
        return redirect("create_recipe_tags")
    return redirect("update_recipe_tags", recipe_id=handler.recipe_id)


def show_success_message(request, handler, recipe):
    if handler.is_create_mode:
        messages.success(request, "Recipe created successfully!")
        return

    if handler.is_owner:
        messages.success(request, f"Successfully updated recipe: {recipe.title}")
        return

    messages.success(request, f"Created your modified version: {recipe.title}")
