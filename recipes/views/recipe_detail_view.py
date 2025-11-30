from recipes.models.recipe import Recipe
from django.http import Http404
from django.shortcuts import render
import re
import openai
import json
from django.http import JsonResponse
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
        'scaled_ingredients': scaled_ingredients,
        'desired_servings': desired_servings,
        'scaling_factor': scaling_factor,
        'steps': recipe.get_step_list(),
        'course_tags': recipe.get_course_tags_list(),
        'dietary_tags': recipe.get_dietary_tags_list(),
        'cuisine_tags': recipe.get_cuisine_tags_list(),
        'other_tags': recipe.get_other_tags_list(),
        'prep_time_display': recipe.get_prep_time_display(),
        'cook_time_display': recipe.get_cook_time_display(),
        'total_prep_minutes': recipe.get_total_prep_time_minutes(),
        'total_cook_minutes': recipe.get_total_cook_time_minutes(),
        'total_time_display' : recipe.get_total_time_display(),
        'user_has_flagged': user_has_flagged,
        'is_owner': recipe.author == request.user,
        'cost_estimate': cost_estimate,
        'cost_error': cost_error,
    }
   
    return render(request, 'recipes/recipe.html', context)

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

# Get cost estimate data from AI for given ingredients and servings
def get_cost_estimate_data(scaled_ingredients, servings):
    ingredients_text = '\n'.join(scaled_ingredients)
    ai_prompt = f"""Estimate the total cost in GBP (£) for these ingredients for {servings} servings:

    {ingredients_text}

    Provide response as JSON:
    {{
        "total_cost": <number>,
        "cost_per_serving": <number>,
        "currency": "GBP"
    }}

    Use typical UK supermarket prices. Return only JSON."""
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Estimate recipe costs in GBP. Return only JSON."},
                {"role": "user", "content": ai_prompt}
            ],
            temperature=0.3,
            max_tokens=150,
            timeout=30
        )
        
        ai_response = response.choices[0].message.content.strip()
        cost_data = json.loads(ai_response)
        
        return {
            'total_cost': cost_data['total_cost'],
            'cost_per_serving': cost_data['cost_per_serving'],
            'servings': servings
        }
        
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")