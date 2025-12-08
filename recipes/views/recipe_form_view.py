from django.contrib.auth.decorators import login_required
from recipes.handlers.recipe_form_handler import RecipeFormHandler


@login_required
def recipe_form_view(request, recipe_id=None):
    """
    Step 1: Basic form fields (not tags)
    
    If recipe_id is None: create a recipe
    Otherwise: update an existing recipe
    """

    handler = RecipeFormHandler(request, recipe_id)

    if request.method == 'POST':
        return handler.handle_form_post()
    return handler.handle_form_get()