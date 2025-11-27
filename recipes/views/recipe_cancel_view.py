from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from recipes.helpers.recipe_form_helpers import cleanup_temp_image

@login_required
def cancel_recipe_operation(request, recipe_id=None):
    """
    Cancel recipe create/update and cleanup session data
    If recipe_id is None: Cancel create (redirect to all_recipes)
    else: cancel update (redirect to recipe_detail)
    """
    session_key = 'recipe_form_data' if recipe_id is None else f'recipe_update_{recipe_id}'

    # Cleanup temp giles
    if session_key in request.session:
        session_data = request.session[session_key]
        cleanup_temp_image(session_data.get('temp_image_path'))
        del request.session[session_key]

    request.session.modified = True

    # Show message and redirect
    if recipe_id is None:
        messages.info(request, 'Recipe creation cancelled')
        return redirect('all_recipes')
    
    else:
        messages.info(request, 'Recipe update cancelled')
        return redirect('recipe_detail', recipe_id=recipe_id)
    