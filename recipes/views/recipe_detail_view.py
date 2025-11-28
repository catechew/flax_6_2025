from recipes.models.recipe import Recipe
from django.http import Http404
from django.shortcuts import render
import re
from recipes.models.rating import Rating

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

    # scale ingredients if needed
    scaled_ingredients = []
    for ingredient in recipe.get_ingredient_list():
        scaled_ingredient = scale_ingredient(ingredient, scaling_factor)
        scaled_ingredients.append(scaled_ingredient)
    
    # Retrieve logged in user's rating for the recipe
    user_rating = None
    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(recipe=recipe, user=request.user).first()
    
    context = {
        'recipe': recipe,
        'scaled_ingredients': scaled_ingredients,
        'desired_servings': desired_servings,
        'scaling_factor': scaling_factor,
        'steps' : recipe.get_step_list(),
        'course_tags': recipe.get_course_tags_list(),
        'dietary_tags': recipe.get_dietary_tags_list(),
        'cuisine_tags': recipe.get_cuisine_tags_list(),
        'other_tags': recipe.get_other_tags_list(),
        'prep_time_display': recipe.get_prep_time_display(),
        'cook_time_display': recipe.get_cook_time_display(),
        'total_prep_minutes': recipe.get_total_prep_time_minutes(),
        'total_cook_minutes': recipe.get_total_cook_time_minutes(),
        'total_time_display' : recipe.get_total_time_display(),
        'is_owner': recipe.author == request.user,
    }
   
    return render(request, 'recipe.html', context)

# Scale ingredient quantities by the given factor
def scale_ingredient(ingredient, factor):
    # Pattern to match numbers (including decimals and fractions)
    pattern = r'(\d+/\d+|\d+\.?\d*)'

    def replace_number(match):
        number_str = match.group(1)

        # Handle fractions
        if '/' in number_str:
            parts = number_str.split('/')
            number = float(parts[0]) / float(parts[1])
        else:
            number = float(number_str)
        
        # Scale the number
        scaled = number * factor

        if scaled == int(scaled):
            return str(int(scaled))
        else:
            return f"{scaled:.1f}"
    return re.sub(pattern, replace_number, ingredient)