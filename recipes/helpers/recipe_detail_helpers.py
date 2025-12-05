import re
from recipes.models import Rating, Flag
import openai
import json

def scale_ingredient(ingredient, factor):
    """
    Scale ingredient quantities by the given factor
    """

    # Pattern to match numbers (including decimals and fractions)
    pattern = r'(\d+/\d+|\d+\.?\d*)'

    def replace_number(match):
        number_str = match.group(1)
        number = get_new_number(number_str) if '/' in number_str else float(number_str)
        scaled = number * factor
        
        return format_scaled_number(scaled)
        
    return re.sub(pattern, replace_number, ingredient)

def format_scaled_number(number):
    if number.is_integer():
        return str(int(number))
    else:
        return f"{number:.1f}"

def get_new_number(number_str):
    parts = number_str.split('/')
    number = float(parts[0]) / float(parts[1])
    return number

def get_scaled_ingredients_context(recipe, desired_servings):
    if desired_servings <= 0:
        desired_servings = recipe.servings

    scaling_factor = desired_servings/recipe.servings

    scaled_ingredients = [
        scale_ingredient(ingredient, scaling_factor)
        for ingredient in recipe.get_ingredient_list()
    ]

    return {
        'scaled_ingredients':scaled_ingredients,
        'desired_servings':desired_servings,
        'scaling_factor':scaling_factor,
    }

def get_user_rating(recipe, user):
    # Retrieve logged in user's rating for the recipe
    if not user.is_authenticated:
        return None
    try: 
        return Rating.objects.filter(recipe=recipe, user=user).first()
    except Rating.DoesNotExist:
        return None
     

def has_user_flagged_recipe(recipe, user):
    if not user.is_authenticated:
        return False
   
    return Flag.objects.filter(recipe=recipe, user=user).exists()

def get_recipe_tag_display_context(recipe):
    """ Returns tag display context from recipe model. """
    return {
        'course_tags': recipe.get_course_tags_list(),
        'dietary_tags': recipe.get_dietary_tags_list(),
        'cuisine_tags': recipe.get_cuisine_tags_list(),
        'other_tags': recipe.get_other_tags_list(),
    }

def get_recipe_time_display_context(recipe):
    """ Return recipe time display context from recipe model. """
    return {
        'prep_time_display': recipe.get_prep_time_display(),
        'cook_time_display': recipe.get_cook_time_display(),
        'total_time_display' : recipe.get_total_time_display(),
        'total_cook_minutes' : recipe.get_total_cook_time_minutes(),
        'total_prep_minutes' : recipe.get_total_prep_time_minutes(),
    }

def create_cost_prompt(scaled_ingredients, servings):
    """ Create AI prompt for cost estimation. """
    ingredients_text = '\n'.join(scaled_ingredients)
    return f"""Estimate the total cost in GBP (£) for these ingredients for {servings} servings:

    {ingredients_text}

    Provide response as JSON:
    {{
        "total_cost": <number>,
        "cost_per_serving": <number>,
        "currency": "GBP"
    }}

    Use typical UK supermarket prices. Return only JSON."""


def call_openai_for_cost(prompt):
    """ Call OpenAI API for cost estimation. """
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Estimate recipe costs in GBP. Return only JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=150,
        timeout=30
    )
    return response.choices[0].message.content.strip()

def parse_cost_response(ai_response, servings):
    """ Parse AI response and extract cost data. """
    cost_data = json.loads(ai_response)
    return {
        'total_cost': cost_data['total_cost'],
        'cost_per_serving': cost_data['cost_per_serving'],
        'servings': servings
    }

def get_cost_estimate_data(scaled_ingredients, servings):
    """ Get cost estimate data using AI. """
    try:
        prompt = create_cost_prompt(scaled_ingredients, servings)
        ai_response = call_openai_for_cost(prompt)
        return parse_cost_response(ai_response, servings)
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")