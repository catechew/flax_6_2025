from recipes.models.recipe import Recipe
from django.http import Http404
from django.shortcuts import render
import re

def recipe_detail(request, recipe_id):
    try:
        recipe = Recipe.objects.get(id=recipe_id)
    except Recipe.DoesNotExist:
        raise Http404(f"Could not find recipe with primary key {recipe_id}") 
    
    # Get desired servings from GET parameter, default to recipe's servings
    desired_servings = int(request.GET.get('servings', recipe.servings))

    # Calculate scaling factor
    scaling_factor = desired_servings / recipe.servings

    # scale ingredients if needed
    scaled_ingredients = []
    for ingredient in recipe.get_ingredient_list():
        scaled_ingredient = scale_ingredient(ingredient, scaling_factor)
        scaled_ingredients.append(scaled_ingredient)
    
    context = {
        'recipe': recipe,
        'scaled_ingredients': scaled_ingredients,
        'desired_servings': desired_servings,
        'scaling_factor': scaling_factor,
        'steps' : recipe.get_step_list(),
    }
   
    return render(request, 'recipe.html', context)

# Scale ingredient quantities by the given factor
def scale_ingredient(ingredient, factor):
    # pattern to match numbers (including decimals and fractions)
    pattern = r'(\d+\.?\d*|\d+/\d+)'

    def replace_number(match):
        number_str = match.group(1)

        # Handle fractions
        if '/' in number_str:
            parts = number_str.split('/')
            number = float(parts[0]) / float(parts[1])
        else:
            number = float(number_str)
        
        # scale the number
        scaled = number * factor

        if scaled == int(scaled):
            return str(int(scaled))
        else:
            return f"{scaled:.1f}"
    return re.sub(pattern, replace_number, ingredient)