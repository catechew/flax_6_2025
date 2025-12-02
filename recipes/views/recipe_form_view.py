from django.contrib.auth.decorators import login_required
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
        return handler.handle_form_post()
    
    # Handle GET - display form
    return handler.handle_form_get()




