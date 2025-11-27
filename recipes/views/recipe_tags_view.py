from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from recipes.models import Recipe
from recipes.forms.recipe_form import RecipeForm
from django.http import QueryDict
from django.core.files.base import ContentFile
from django.core.files import File
from recipes.helpers.recipe_form_helpers import (
    get_tag_action_from_request, 
    handle_tag_operation, 
    get_tag_context, 
    apply_tags_to_recipe,
    load_temp_image,
    cleanup_temp_image
)

def get_session_key(recipe_id=None):
    """Generate session key for create or update mode"""
    return 'recipe_form_data' if recipe_id is None else f'recipe_update_{recipe_id}'

def handle_tag_action(request, session_data, recipe_id):
    """
    Handle tag add/remove actions
    Returns redirect if action was handled
    """
    action, category, value = get_tag_action_from_request(request)

    if not action:
        return None
    
    # Perform tag operation
    if handle_tag_operation(session_data, action, category, value):
        request.session.modified = True

    # Redirect back to same page
    if recipe_id is None:
        return redirect('create_recipe_tags')
    return redirect('update_recipe_tags', recipe_id=recipe_id)

def save_recipe_with_tags(form, session_data, user, original_recipe, is_owner):
    """Save recipe with tags and handle image operations"""
    recipe = form.save(commit=False)

    # Set author for new recipes (create or non-owner copy)
    if original_recipe and not is_owner:
        recipe.pk = None
        recipe.id = None
        recipe.author = user

        # Copy original image for non-owner modifications
        if original_recipe.image:
            recipe.image.save(
                original_recipe.image.name,
                ContentFile(original_recipe.image.file.read()),
                save=False
            )

    # For create mode
    elif not original_recipe:
        recipe.author = user
    
    # Handle image deletion (owner only)
    if original_recipe and is_owner and session_data.get('image_clear'):
        if recipe.image:
            recipe.image.delete(save=False)
            recipe.image = None

    # Apply tags
    apply_tags_to_recipe(recipe, session_data)

    recipe.save()
    return recipe

def cleanup_session(session_key, session_data, request):
    """Cleanup temporary files and session data"""
    cleanup_temp_image(session_data.get('temp_image_path'))

    if session_key in request.session:
        del request.session[session_key]
    request.session.modified = True

def show_success_message(request, mode, is_owner, recipe, original_recipe):
    if mode == "create":
        messages.success(request, 'Recipe created successfully!')
    elif is_owner:
        messages.success(request, f'Successfully update recipe: {recipe.title}')
    else:
        messages.success(request, f'Created your modified version: {recipe.title}')
        if original_recipe:
            messages.info(request, f'Original recipe by {original_recipe.author.username} was not changed.')

def finalise_recipe(request, session_data, session_key, recipe, is_owner, mode):
    """Create or update the recipe the form data and tags"""

    # Recreate form with saved data
    form_data = QueryDict('', mutable=True)
    form_data.update(session_data['form_data'])

    # Handle image file
    files = load_temp_image(
        session_data.get('temp_image_path'),
        request.user.id,
        recipe.id if recipe else None
    )

    # Create form with instance (if available)
    if recipe and is_owner:
        form = RecipeForm(form_data, files, instance=recipe)
    else:
        form = RecipeForm(form_data, files)
    
    if not form.is_valid():
        messages.error(request, 'There was an error with your recipe. Please check the form.')
        if mode == 'create':
            return redirect('create_recipe')
        return redirect('update_recipe', recipe_id=recipe.id)
    
    # Save recipe
    try:
        saved_recipe = save_recipe_with_tags(
            form, session_data, request.user, recipe, is_owner
        )

        # Cleanup and show success
        cleanup_session(session_key, session_data, request)
        show_success_message(request, mode, is_owner, saved_recipe, recipe)
        print(f"DEBUG: Redirecting to recipe {saved_recipe.id}")
        return redirect('recipe_detail', recipe_id=saved_recipe.id)
    
    except Exception as e:
        messages.error(request, f'Error saving recipe: {str(e)}')
        if mode == 'create':
            return redirect('create_recipe')
        return redirect('update_recipe', recipe_id=recipe.id)

def build_tags_context(session_data, recipe, mode, is_owner):
    """Build template context for tags page"""
    # Get tag data from helper
    context = get_tag_context(session_data)
    context.update({
        'is_owner' : is_owner,
        'mode' : mode,
        'has_image' : 'temp_image_path' in session_data
    })

    # Add recipe info if updating
    if recipe:
        context['recipe'] = recipe
        context['recipe_id'] = recipe.id

    return context

@login_required
def recipe_tags_view(request, recipe_id=None):
    """
    Step 2: Tags
    If recipe_id is None: create
    else: update
    """

    # Determine if create or update
    mode = 'create' if recipe_id is None else 'update'
    recipe = get_object_or_404(Recipe, id=recipe_id) if recipe_id else None

    # Get session data
    session_key = get_session_key(recipe_id)

    # Redirect to step 1 if no form data
    if session_key not in request.session or 'form_data' not in request.session[session_key]:
        messages.warning(request, 'Please fill in the recipe details first.')
        if mode == 'create':
            return redirect('create_recipe')
        return redirect('update_recipe', recipe_id=recipe_id)
    
    session_data = request.session[session_key]
    is_owner = session_data.get('is_owner', True)

    # Handle tag operations (add/remove)
    if request.method == 'POST':
        # Check if this is a tag action (not final submit)
        if 'create_recipe' not in request.POST and 'update_recipe' not in request.POST:
            tag_redirect = handle_tag_action(request, session_data, recipe_id)
            if tag_redirect:
                return tag_redirect
    
        # Handle recipe creation/update
        else:
            return finalise_recipe(request, session_data, session_key, recipe, is_owner, mode)
        
    # Display tag selection page
    context = build_tags_context(session_data, recipe, mode, is_owner)
    return render(request, 'recipe_tags_form.html', context)
        
