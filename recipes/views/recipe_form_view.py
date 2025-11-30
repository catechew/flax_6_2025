from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from recipes.models import Recipe
from recipes.forms.recipe_form import RecipeForm
from recipes.helpers.recipe_form_helpers import save_temp_image
from recipes.handlers.recipe_form_handler import RecipeFormHandler

@login_required
def recipe_form_view(request, recipe_id=None):
    """
    Step 1: Basic form fields (not tags)
    If recipe_id is None: Create
    else: Update
    """

    handler = RecipeFormHandler(request, recipe_id)

    # Handle POST - form submission
    if request.method == 'POST':
        return handle_form_post(request, handler)
    
    # Handle GET - display form
    return handle_form_get(request, handler)

def handle_form_post(request, handler):
    """Handle form submission"""
    # Create form with instance (if available)
    form = handler.create_form(request.POST, request.FILES)

    if not form.is_valid():
        context = handler.get_form_context(form)
        return render(request, 'partials/recipe_form.html', context)

    # Save form data to session
    save_form_to_session(request, handler.session_data)

    # Handle image upload
    handle_image_in_session(request, handler.session_data, handler.recipe)

    handler.mark_session_modified()

    # Redirect to tags page
    return handler.redirect_to_tags_page()

def handle_form_get(request, handler):
    """Handle form display"""
    # Pre-populate form if coming back from tags page
    if 'form_data' in handler.session_data:
        form = handler.create_form(handler.session_data['form_data'])
    else:
        form = handler.create_form()

    context = handler.get_form_context(form)
    return render(request, 'partials/recipe_form.html', context)

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


