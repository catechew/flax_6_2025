from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from recipes.models import Recipe
from recipes.forms.recipe_form import RecipeForm
from django.http import QueryDict
from recipes.helpers.recipe_form_helpers import initialise_tag_session, save_temp_image, cleanup_temp_image

def get_session_key(recipe_id=None):
    """Generate session key for create or update mode"""
    return 'recipe_form_data' if recipe_id is None else f'recipe_update_{recipe_id}'

def initialise_session_data(request, recipe=None):
    """Initialise or retrieve session data for recipe form"""
    session_key = get_session_key(recipe.id if recipe else None)

    if session_key not in request.session:
        request.session[session_key] = {}
        initialise_tag_session(request.session[session_key], recipe)

        if recipe: #Update mode
            request.session[session_key]['is_owner'] = recipe.author == request.user
            request.session[session_key]['original_author'] = recipe.author.username
        
    return request.session[session_key], session_key

@login_required
def recipe_form_view(request, recipe_id=None):
    """
    Step 1: Basic form fields (not tags)
    If recipe_id is None: Create
    else: Update
    """
    # Determine if create or update
    mode = 'create' if recipe_id is None else 'update'
    recipe = get_object_or_404(Recipe, id=recipe_id) if recipe_id else None

    # Initialise session
    session_data, session_key = initialise_session_data(request, recipe)
    is_owner = session_data.get('is_owner', True)

    # Handle POST - form submission
    if request.method == 'POST':
        return handle_form_post(request, recipe, session_data, session_key, is_owner, mode)
    
    # Handle GET - display form
    return handle_form_get(request, recipe, session_data, mode, is_owner)

    

