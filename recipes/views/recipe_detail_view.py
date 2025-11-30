from recipes.models.recipe import Recipe
from django.http import Http404
from recipes.models.rating import Rating
from recipes.models.flag import Flag

# Display recipe details with optional cost estimation
def recipe_detail(request, recipe_id):
    try:
        recipe = Recipe.objects.get(id=recipe_id)
    except Recipe.DoesNotExist:
        raise Http404(f"Could not find recipe with primary key {recipe_id}") 
    
    # Get desired servings from GET parameter, default to recipe's servings
    servings_input = request.GET.get('servings', recipe.servings)
    try:
        desired_servings = int(servings_input) if servings_input else recipe.servings
    except (ValueError, TypeError):
        desired_servings = recipe.servings

    # Calculate scaling factor
    scaling_factor = desired_servings / recipe.servings

    # Scale ingredients if needed
    scaled_ingredients = []
    for ingredient in recipe.get_ingredient_list():
        scaled_ingredient = scale_ingredient(ingredient, scaling_factor)
        scaled_ingredients.append(scaled_ingredient)
    
    # Retrieve logged in user's rating for the recipe
    user_rating = None
    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(recipe=recipe, user=request.user).first()

    # Check if user has flagged a recipe
    user_has_flagged = False
    if request.user.is_authenticated:
        user_has_flagged = Flag.objects.filter(recipe=recipe, user=request.user).exists()
    
    # Handle cost estimation if requested
    cost_estimate = None
    cost_error = None
    if request.GET.get('show_cost') == 'true':
        try:
            cost_estimate = get_cost_estimate_data(scaled_ingredients, desired_servings)
        except Exception as e:
            cost_error = str(e)
    
    context = {
        'recipe': recipe,
        'steps': recipe.get_step_list(
        'user_has_flagged': user_has_flagged,
        'is_owner': recipe.author == request.user,
        'cost_estimate': cost_estimate,
        'cost_error': cost_error,
    }
   
    return render(request, 'recipes/recipe.html', context)


