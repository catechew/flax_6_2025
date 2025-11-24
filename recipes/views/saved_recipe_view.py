from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from recipes.models.recipe import Recipe

@login_required
def toggle_save_recipe(request, recipe_id):
    """
    Toggle adding/removing a recipe from the user's saved list.
    Redirects back to the page the user came from.
    """
    recipe = get_object_or_404(Recipe, id=recipe_id)
    
    if request.user in recipe.saved_by.all():
        recipe.saved_by.remove(request.user)
    else:
        recipe.saved_by.add(request.user)
        
    # Redirect back to the previous page (e.g., all_recipes or recipe_detail)
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))


@login_required
def saved_recipe_list(request):
    """
    Display recipes saved by the current user.
    """
    current_user = request.user
    
    # Access the recipes via the related_name we defined in the model
    saved_recipes = current_user.saved_recipes.all().order_by('-publication_date')

    return render(request, 'saved_recipes.html', {
        'user': current_user,
        'recipes': saved_recipes,
    })