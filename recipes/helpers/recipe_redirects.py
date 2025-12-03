from django.contrib import messages
from django.shortcuts import redirect


def redirect_to_form(handler):
    return redirect(
        "create_recipe" if handler.is_create_mode
        else "update_recipe",
        recipe_id=handler.recipe_id,
    )

def redirect_to_tags(handler):
    return redirect(
        "create_recipe_tags" if handler.is_create_mode
        else "update_recipe_tags",
        recipe_id=handler.recipe_id,
    )

def show_success_message(request, handler, recipe):
    if handler.is_create_mode:
        messages.success(request, "Recipe created successfully!")
    elif handler.is_owner:
        messages.success(request, f"Successfully updated recipe: {recipe.title}")
    else:
        messages.success(request, f"Created your modified version: {recipe.title}")
