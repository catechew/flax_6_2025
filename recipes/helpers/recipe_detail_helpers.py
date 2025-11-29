import re
from recipes.models import Rating, Flag

def scale_ingredient(ingredient, factor):
    """
    Scale ingredient quantities by the given factor
    """

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
    # Check if user has flagged a recipe
    if not user.is_authenticated:
        return False
   
    return Flag.objects.filter(recipe=recipe, user=user).exists()

def get_recipe_tag_display_context(recipe):
    """
    returns tag display context from recipe model
    """
    return {
        'course_tags': recipe.get_course_tags_list(),
        'dietary_tags': recipe.get_dietary_tags_list(),
        'cuisine_tags': recipe.get_cuisine_tags_list(),
        'other_tags': recipe.get_other_tags_list(),
    }

def get_recipe_time_display_context(recipe):
    """
    return recipe time display context from recipe model
    """
    return {
        'prep_time_display': recipe.get_prep_time_display(),
        'cook_time_display': recipe.get_cook_time_display(),
        'total_time_display' : recipe.get_total_time_display(),
    }