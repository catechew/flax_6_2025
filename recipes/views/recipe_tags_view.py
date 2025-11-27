from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from recipes.models import Recipe
from recipes.forms.recipe_form import RecipeForm
from django.http import QueryDict
from django.core.files.base import ContentFile
from recipes.helpers.recipe_form_helpers import (
    get_tag_action_from_request, 
    handle_tag_operation, 
    apply_tags_to_recipe,
    load_temp_image,
    cleanup_session
)
from recipes.handlers.recipe_form_handler import RecipeFormHandler

@login_required
def recipe_tags_view(request, recipe_id=None):
    """
    Step 2: Tags
    If recipe_id is None: create
    else: update
    """

    handler = RecipeFormHandler(request, recipe_id)

    # Redirect to step 1 if no form data
    if 'form_data' not in handler.session_data:
        return handler.show_missing_form_data_warning()

    # Handle tag operations (add/remove)
    if request.method == 'POST':
        # Check if this is a tag action (not final submit)
        if 'create_recipe' not in request.POST and 'update_recipe' not in request.POST:
            tag_redirect = handle_tag_action(request, handler)
            if tag_redirect:
                return tag_redirect
    
        # Handle recipe creation/update
        else:
            return finalise_recipe(request, handler)
        
    # Display tag selection page
    context = handler.get_tags_context()
    return render(request, 'recipe_tags_form.html', context)

def handle_tag_action(request, handler):
    """
    Handle tag add/remove actions
    Returns redirect if action was handled
    """
    action, category, value = get_tag_action_from_request(request)

    if not action:
        return None
    
    # Perform tag operation
    if handle_tag_operation(handler.session_data, action, category, value):
        handler.mark_session_modified()

    return handler.redirect_to_tags_page()

def _prepare_recipe_author(recipe, user, original_recipe, is_owner):
    """Set appropriate author for recipe based on create/update mode"""
    if original_recipe and not is_owner:
        # non-owner creating a modified version/copy
        recipe.pk = None
        recipe.id = None
        recipe.author = user
    elif not original_recipe:
        # create mode
        recipe.author = user

def _handle_image_copy(recipe, original_recipe):
    """Copy image from original recipe for non-owner modification"""
    if original_recipe.image:
            original_recipe.image.file.seek(0)
            recipe.image.save(
                original_recipe.image.name,
                ContentFile(original_recipe.image.file.read()),
                save=False
            )
            original_recipe.image.file.seek(0) #reset for future use

def _handle_image_deletion(recipe, session_data, original_recipe, is_owner):
    """Delete recipe image"""
    if original_recipe and is_owner and session_data.get('image_clear'):
        if recipe.image:
            recipe.image.delete(save=False)
            recipe.image = None
    
    
def save_recipe_with_tags(form, session_data, user, original_recipe, is_owner):
    """Save recipe with tags and handle image operations"""
    recipe = form.save(commit=False)

    # Set author 
    _prepare_recipe_author(recipe, user, original_recipe, is_owner)

    # Handle image operations
    if original_recipe and not is_owner:
        _handle_image_copy(recipe, original_recipe)
    _handle_image_deletion(recipe, session_data, original_recipe, is_owner)

    # Apply tags
    apply_tags_to_recipe(recipe, session_data)

    recipe.save()
    return recipe

def finalise_recipe(request, handler):
    """Create or update the recipe the form data and tags"""

    # Recreate form with saved data
    form_data = QueryDict('', mutable=True)
    form_data.update(handler.session_data['form_data'])

    # Handle image file
    files = load_temp_image(
        handler.session_data.get('temp_image_path'),
        request.user.id,
        handler.recipe.id if handler.recipe else None
    )

    # Create form with instance (if available)
    form = handler.create_form(form_data, files)
    
    if not form.is_valid():
        messages.error(request, 'There was an error with your recipe. Please check the form.')
        return handler.redirect_to_form_page()
    
    # Save recipe
    try:
        saved_recipe = save_recipe_with_tags(
            form, handler.session_data, request.user, handler.recipe, handler.is_owner
        )

        # Cleanup and show success
        cleanup_session(handler.session_key, handler.session_data, request)
        handler.show_success_message(saved_recipe)
        return handler.redirect_to_detail_page(saved_recipe.id)
    
    except Exception as e:
        messages.error(request, f'Error saving recipe: {str(e)}')
        return handler.redirect_to_form_page()

        
