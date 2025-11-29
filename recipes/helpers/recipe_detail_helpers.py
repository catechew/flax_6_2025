import re
from fractions import Fraction


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