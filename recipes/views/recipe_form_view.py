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

def handle_form_post(request, recipe, session_data, session_key, is_owner, mode):
    # Create form with instance (if available)
    if recipe and is_owner:
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
    else:
        form = RecipeForm(request.POST, request.FILES)

    if not form.is_valid():
        context = build_form_context(form, recipe, mode, is_owner)
        return render(request, 'recipe_form.html', context)

    # Save form data to session
    save_form_to_session(request, session_data)

    # Handle image upload
    handle_image_in_session(request, session_data, recipe)

    request.session.modified = True

    # Redirect to tags page
    if mode == 'create':
        return redirect('create_recipe_tags')

    return redirect('update_recipe_tags', recipe_id=recipe.id)

def handle_form_get(request, recipe, session_data, mode, is_owner):
    # Pre-populate form if coming back from tags page
    if 'form_data' in session_data:
        if recipe and is_owner:
            form = RecipeForm(session_data['form_data'], instance=recipe)
        else:
            form = RecipeForm(session_data['form_data'])

    else:
        form = RecipeForm(instance=recipe) if recipe else RecipeForm()

    context = build_form_context(form, recipe, mode, is_owner)
    return render(request, 'recipe_form.html', context)

def save_form_to_session(request, session_data):
    """Save form data to session""" 
    form_dict = {key: value for key, value in request.POST.items()}
    session_data['form_data'] = form_dict
    session_data['image_clear'] = request.POST.get('image-clear', False)

def handle_image_in_session(request, session_data, recipe):
    """Handle image upload and save to temp location"""
    if request.FILES.get('image'):
        temp_path = save_temp_image(
            request.FILES['image'],
            request.user.id,
            recipe.id if recipe else None
        )
        if temp_path:
            session_data['temp_image_path'] = temp_path
    elif recipe and not recipe.author == request.user and recipe.image:
        # non-owner updating
        session_data['copy_original_image'] = True

def build_form_context(form, recipe, mode, is_owner):
    """Build template context for recipe form"""
    context = {
        'form' : form,
        'mode' : mode,
        'is_owner' : is_owner
    }
    if recipe:
        context['recipe'] = recipe
        context['recipe_id'] = recipe.id
        context['original_author'] = recipe.author.username

    return context

