from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from recipes.models import Recipe
from recipes.forms.recipe_form import RecipeForm

@login_required
def create_recipe(request):
    """
    Recipe creation view with session-based tag management.
    Handles tag selection/removal via form submissions.
    """

    # Initialize session data if not exists
    if 'recipe_form_data' not in request.session:
        request.session['recipe_form_data'] = {
            'course_tags': [],
            'dietary_tags': [],
            'other_tags': [],
        }

    session_data = request.session['recipe_form_data']

    # Handle tag additions
    if request.method == 'POST' and 'add_course_tag' in request.POST:
        tag = request.POST.get('course_tag_value')
        if tag and tag not in session_data['course_tags']:
            session_data['course_tags'].append(tag)
            request.session.modified = True
        return redirect('create_recipe')

    if request.method == 'POST' and 'add_dietary_tag' in request.POST:
        tag = request.POST.get('dietary_tag_value')
        if tag and tag not in session_data['dietary_tags']:
            session_data['dietary_tags'].append(tag)
            request.session.modified = True
        return redirect('create_recipe')

    if request.method == 'POST' and 'add_other_tag' in request.POST:
        tag = request.POST.get('other_tag_value')
        if tag and tag not in session_data['other_tags']:
            session_data['other_tags'].append(tag)
            request.session.modified = True
        return redirect('create_recipe')

    # Handle tag removals
    if request.method == 'POST' and 'remove_course_tag' in request.POST:
        tag = request.POST.get('remove_course_tag')
        if tag in session_data['course_tags']:
            session_data['course_tags'].remove(tag)
            request.session.modified = True
        return redirect('create_recipe')

    if request.method == 'POST' and 'remove_dietary_tag' in request.POST:
        tag = request.POST.get('remove_dietary_tag')
        if tag in session_data['dietary_tags']:
            session_data['dietary_tags'].remove(tag)
            request.session.modified = True
        return redirect('create_recipe')

    if request.method == 'POST' and 'remove_other_tag' in request.POST:
        tag = request.POST.get('remove_other_tag')
        if tag in session_data['other_tags']:
            session_data['other_tags'].remove(tag)
            request.session.modified = True
        return redirect('create_recipe')

    # Handle final recipe creation
    if request.method == 'POST' and 'create_recipe' in request.POST:
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user

            # Set tags from session
            recipe.course_tags = ','.join(session_data['course_tags'])
            recipe.dietary_tags = ','.join(session_data['dietary_tags'])
            recipe.other_tags = ','.join(session_data['other_tags'])

            recipe.save()

            # Clear session data
            del request.session['recipe_form_data']
            request.session.modified = True

            messages.success(request, 'Recipe created successfully!')
            return redirect('recipe_detail', recipe_id=recipe.id)
    else:
        form = RecipeForm()

    # Predefined tag options
    course_options = ['dessert', 'main', 'appetiser', 'breakfast', 'snack']
    dietary_options = ['vegetarian', 'vegan', 'halal', 'kosher', 'gluten-free', 'dairy-free']
    other_options = ['high protein', 'low calorie', 'low carb', 'quick', 'budget']

    context = {
        'form': form,
        'course_tags': session_data['course_tags'],
        'dietary_tags': session_data['dietary_tags'],
        'other_tags': session_data['other_tags'],
        'course_options': course_options,
        'dietary_options': dietary_options,
        'other_options': other_options,
    }

    return render(request, 'create_recipe.html', context)