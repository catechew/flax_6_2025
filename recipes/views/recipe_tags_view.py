from django.shortcuts import render
from django.contrib.auth.decorators import login_required
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
            tag_redirect = handler.handle_tag_action()
            if tag_redirect:
                return tag_redirect
    
        # Handle recipe creation/update
        else:
            return handler.finalise_recipe()
        
    # Display tag selection page
    context = handler.get_tags_context()
    return render(request, 'recipes/recipe_tags_form.html', context)