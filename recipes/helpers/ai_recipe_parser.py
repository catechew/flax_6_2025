import re

"""
Helper functions for parsing AI-generated recipe data.
"""

def parse_time_string(time_str):
    """ Parse '15 minutes' or '1 hour 30 minutes' to total minutes. """
    if not time_str:
        return 0

    time_str = time_str.lower()
    hours = extract_hours(time_str)
    minutes = extract_minutes(time_str)
    return (hours * 60) + minutes

def extract_hours(time_str):
    """ Extract hours from time string. """
    if 'hour' not in time_str:
        return 0
    try:
        parts = time_str.split('hour')[0].strip().split()
        return int(parts[-1]) if parts else 0
    except (ValueError, IndexError):
        return 0

def extract_minutes(time_str):
    """ Extract minutes from time string. """
    if 'min' not in time_str:
        return 0

    parts = time_str.split('min')[0].strip().split()
    return find_last_digit(parts)

def find_last_digit(parts):
    """ Find last digit in list of string parts. """
    return next((int(part) for part in reversed(parts) if part.isdigit()), 0)

def format_ingredients_for_form(ingredients_list):
    """ Convert AI format to app format: '400g spaghetti' → 'Spaghetti (400g)'. """
    formatted = [
        format_single_ingredient(ingredient.strip())
        for ingredient in ingredients_list
        if ingredient.strip()
    ]
    return '\n'.join(formatted)


def format_single_ingredient(ingredient):
    """Format single ingredient line."""
    match = try_parse_ingredient(ingredient)

    if match:
        return format_matched_ingredient(match)
    return f"{ingredient} (as needed)"

def try_parse_ingredient(ingredient):
    """Try to parse ingredient with regex."""
    pattern = r'^([\d./]+\s*(?:g|kg|ml|l|tsp|tbsp|cup|cups|oz|lb|cloves?|pieces?)?)\s+(.+)$'
    return re.match(pattern, ingredient, re.IGNORECASE)

def format_matched_ingredient(match):
    """ Format parsed ingredient match. """
    quantity = match.group(1).strip()
    name = match.group(2).strip()
    name = capitalise_first(name)
    return f"{name} ({quantity})"

def capitalise_first(text):
    """ Capitalise first letter. """
    return text[0].upper() + text[1:] if text else text

def parse_ai_recipe_data(ai_data):
    """ Parse AI data into form-ready format. """
    prep_minutes = parse_time_string(ai_data.get('prep_time', ''))
    cook_minutes = parse_time_string(ai_data.get('cook_time', ''))

    prep_hours, prep_mins = divmod(prep_minutes, 60)
    cook_hours, cook_mins = divmod(cook_minutes, 60)

    return {
        'title': ai_data.get('title', ''),
        'ingredients': format_ingredients_for_form(ai_data.get('ingredients', [])),
        'steps': '\n'.join(ai_data.get('steps', [])),
        'prep_time_hours': prep_hours,
        'prep_time_minutes': prep_mins,
        'cook_time_hours': cook_hours,
        'cook_time_minutes': cook_mins,
        'servings': ai_data.get('servings', 4),
        'ai_dietary_info': ai_data.get('dietary_info', []),
        'ai_description': ai_data.get('description', ''),
    }

def get_dietary_tag_mapping():
    """ Get AI dietary tag to system tag mapping. """
    return {
        'vegetarian': 'Vegetarian',
        'vegan': 'Vegan',
        'gluten-free': 'Gluten-Free',
        'dairy-free': 'Dairy-Free',
        'halal': 'Halal',
        'kosher': 'Kosher',
    }

def map_ai_dietary_tags(ai_dietary_list):
    """ Map AI dietary tags to system tags. """
    mapping = get_dietary_tag_mapping()
    mapped_tags = [
        mapping[ai_tag.lower()]
        for ai_tag in ai_dietary_list
        if ai_tag.lower() in mapping
    ]
    return mapped_tags