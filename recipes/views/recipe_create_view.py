from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from recipes.models import Recipe
from recipes.forms.recipe_form import RecipeForm
import os
from django.http import QueryDict
from django.core.files.uploadedfile import SimpleUploadedFile

@login_required
def create_recipe(request):
    """
    Page 1: Basic recipe information
    """

    # Initialize session data if not exists
    if 'recipe_form_data' not in request.session:
        request.session['recipe_form_data'] = {
            'course_tags': [],
            'dietary_tags': [],
            'other_tags': [],
        }

    session_data = request.session['recipe_form_data']

    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            # Save form data to session (excluding file)
            form_dict = {}
            for key, value in request.POST.items():
                form_dict[key] = value

            session_data['form_data'] = form_dict

            # Handle file upload - save temporarily to disk
            if request.FILES.get('image'):
                uploaded_file = request.FILES['image']
                # Save to temporary location
                temp_filename = f'temp_{request.user.id}_{uploaded_file.name}'
                temp_path = default_storage.save(f'temp/{temp_filename}', ContentFile(uploaded_file.read()))
                session_data['temp_image_path'] = temp_path

            request.session.modified = True

            # Redirect to page 2 (tag selection)
            return redirect('create_recipe_tags')
    else:
        # Pre-populate if coming back from page 2
        if 'form_data' in session_data:
            form = RecipeForm(session_data['form_data'])
        else:
            form = RecipeForm()

    context = {
        'form': form,
    }

    return render(request, 'create_recipe.html', context)


@login_required
def create_recipe_tags(request):
    """
    Page 2: Tag selection and final creation
    """

    # Redirect to page 1 if no form data in session
    if 'recipe_form_data' not in request.session or 'form_data' not in request.session['recipe_form_data']:
        messages.warning(request, 'Please fill in the recipe details first.')
        return redirect('create_recipe')

    session_data = request.session['recipe_form_data']

    # Handle tag additions
    if request.method == 'POST' and 'add_course_tag' in request.POST:
        tag = request.POST.get('add_course_tag')
        if tag and tag not in session_data['course_tags']:
            session_data['course_tags'].append(tag)
            request.session.modified = True
        return redirect('create_recipe_tags')

    if request.method == 'POST' and 'add_dietary_tag' in request.POST:
        tag = request.POST.get('add_dietary_tag')
        if tag and tag not in session_data['dietary_tags']:
            session_data['dietary_tags'].append(tag)
            request.session.modified = True
        return redirect('create_recipe_tags')

    if request.method == 'POST' and 'add_other_tag' in request.POST:
        tag = request.POST.get('add_other_tag')
        if tag and tag not in session_data['other_tags']:
            session_data['other_tags'].append(tag)
            request.session.modified = True
        return redirect('create_recipe_tags')

    # Handle custom tag additions
    if request.method == 'POST' and 'add_course_tag_custom' in request.POST:
        tag = request.POST.get('course_tag_value')
        if tag and tag not in session_data['course_tags']:
            session_data['course_tags'].append(tag)
            request.session.modified = True
        return redirect('create_recipe_tags')

    if request.method == 'POST' and 'add_dietary_tag_custom' in request.POST:
        tag = request.POST.get('dietary_tag_value')
        if tag and tag not in session_data['dietary_tags']:
            session_data['dietary_tags'].append(tag)
            request.session.modified = True
        return redirect('create_recipe_tags')

    if request.method == 'POST' and 'add_other_tag_custom' in request.POST:
        tag = request.POST.get('other_tag_value')
        if tag and tag not in session_data['other_tags']:
            session_data['other_tags'].append(tag)
            request.session.modified = True
        return redirect('create_recipe_tags')

    # Handle tag removals
    if request.method == 'POST' and 'remove_course_tag' in request.POST:
        tag = request.POST.get('remove_course_tag')
        if tag in session_data['course_tags']:
            session_data['course_tags'].remove(tag)
            request.session.modified = True
        return redirect('create_recipe_tags')

    if request.method == 'POST' and 'remove_dietary_tag' in request.POST:
        tag = request.POST.get('remove_dietary_tag')
        if tag in session_data['dietary_tags']:
            session_data['dietary_tags'].remove(tag)
            request.session.modified = True
        return redirect('create_recipe_tags')

    if request.method == 'POST' and 'remove_other_tag' in request.POST:
        tag = request.POST.get('remove_other_tag')
        if tag in session_data['other_tags']:
            session_data['other_tags'].remove(tag)
            request.session.modified = True
        return redirect('create_recipe_tags')

    # Handle final recipe creation
    if request.method == 'POST' and 'create_recipe' in request.POST:
        # Recreate form with saved data
        form_data = QueryDict('', mutable=True)
        form_data.update(session_data['form_data'])

        # Handle image if it exists
        files = {}
        if 'temp_image_path' in session_data:
            temp_path = session_data['temp_image_path']
            if default_storage.exists(temp_path):
                # Read the temp file
                with default_storage.open(temp_path, 'rb') as f:
                    filename = os.path.basename(temp_path).replace(f'temp_{request.user.id}_', '')
                    files = {'image': SimpleUploadedFile(filename, f.read())}

        form = RecipeForm(form_data, files)

        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user

            # Set tags from session
            recipe.course_tags = ','.join(session_data['course_tags'])
            recipe.dietary_tags = ','.join(session_data['dietary_tags'])
            recipe.other_tags = ','.join(session_data['other_tags'])

            recipe.save()

            # Delete temp image file if it exists
            if 'temp_image_path' in session_data:
                temp_path = session_data['temp_image_path']
                if default_storage.exists(temp_path):
                    default_storage.delete(temp_path)

            # Clear session data
            del request.session['recipe_form_data']
            request.session.modified = True

            messages.success(request, 'Recipe created successfully!')
            return redirect('recipe_detail', recipe_id=recipe.id)
        else:
            # If validation fails, show errors
            messages.error(request, 'There was an error creating your recipe. Please check the form.')
            return redirect('create_recipe')

    # Predefined tag options
    course_options = ['dessert', 'main', 'appetiser', 'breakfast', 'snack']
    dietary_options = ['vegetarian', 'vegan', 'halal', 'kosher', 'gluten-free', 'dairy-free']
    other_options = ['high protein', 'low calorie', 'low carb', 'quick', 'budget']

    context = {
        'course_tags': session_data['course_tags'],
        'dietary_tags': session_data['dietary_tags'],
        'other_tags': session_data['other_tags'],
        'course_options': course_options,
        'dietary_options': dietary_options,
        'other_options': other_options,
        'has_image': 'temp_image_path' in session_data,
    }

    return render(request, 'create_recipe_tags.html', context)


@login_required
def cancel_recipe_creation(request):
    """Clear session data and redirect to home"""
    if 'recipe_form_data' in request.session:
        # Clean up temp image file if it exists
        session_data = request.session['recipe_form_data']
        if 'temp_image_path' in session_data:
            temp_path = session_data['temp_image_path']
            if default_storage.exists(temp_path):
                default_storage.delete(temp_path)

        del request.session['recipe_form_data']

    request.session.modified = True
    messages.info(request, 'Recipe creation cancelled.')
    return redirect('all_recipes')

