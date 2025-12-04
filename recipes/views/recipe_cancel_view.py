from django.contrib.auth.decorators import login_required
from recipes.handlers.recipe_form_handler import RecipeFormHandler
from recipes.helpers.recipe_form_helpers import cleanup_session

@login_required
def cancel_recipe_operation(request, recipe_id=None):
    """
    Cancel recipe create/update and cleanup session data
    If recipe_id is None: Cancel create (redirect to all_recipes)
    else: cancel update (redirect to recipe_detail)
    """
    handler = RecipeFormHandler(request, recipe_id)

    # Cleanup temp files
    if handler.session_key in request.session:
        cleanup_session(handler.session_key, handler.session_data, request)

    # Show message and redirect
    return handler.redirect_to_cancel_destination()
    