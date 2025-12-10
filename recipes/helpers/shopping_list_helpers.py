from collections import defaultdict

""" 
Shopping list generation and categorisation. 
"""

INGREDIENT_CATEGORIES = {
    '🧀 Dairy & Eggs': ['cheese', 'cheddar', 'butter', 
                       'milk', 'egg', 'halloumi', 
                       'tofu', 'bread', 'yogurt'],
    
    '🍎 Fruits': ['apple', 'banana', 'lemon', 
                 'strawberries', 'blueberries'],
    
    '🥬 Vegetables': ['avocado', 'onion', 'garlic', 
                     'tomatoes', 'lemon', 'spinach', 
                     'ginger', 'broccoli', 'bell pepper', 
                     'mushrooms', 'cauliflower', 'cucumber'],

     '🌾 Grains & Pasta': ['rice', 'flour', 'penne', 
                         'pasta', 'beans', 'chickpeas'],
    
    '🥩 Meat & Poultry': ['chicken', 'beef'],
    
    '🐟 Seafood': ['salmon', 'tuna'],
    
    '🌶️ Spices & Herbs': ['black pepper', 'basil', 'leaves', 
                          'cilantro', 'chili'],
    
    '🧂 Condiments': ['oil', 'sugar', 'sauce', 
                     'sauce', 'salt', 'pepper'],
}

CATEGORY_ORDER = [
    '🧀 Dairy & Eggs',
    '🍎 Fruits',
    '🥬 Vegetables',
    '🌾 Grains & Pasta',
    '🥩 Meat & Poultry',
    '🐟 Seafood',
    '🧂 Condiments',
    '🌶️ Spices & Herbs',
    '🛒 Other Items',
]

def categorise_ingredient(ingredient):
    """ Categorise ingredient by type. """
    ingredient_lower = ingredient.lower()
    matched_category = next(
        (category for category, keywords in INGREDIENT_CATEGORIES.items()
         if _matches_category(ingredient_lower, keywords)),
        '🛒 Other Items'  
    )
    return matched_category

def _matches_category(ingredient_lower, keywords):
    """ Check if ingredient matches any keyword. """
    return any(keyword in ingredient_lower for keyword in keywords)

def extract_ingredients(slots):
    """ Extract all ingredients from meal slots. """
    shopping_list = defaultdict(list)
    for slot in slots:
        _add_recipe_ingredients(shopping_list, slot)
    return shopping_list

def _add_recipe_ingredients(shopping_list, slot):
    """ Add ingredients from a single recipe slot. """
    recipe = slot.recipe
    ingredients = _get_cleaned_ingredients(recipe)
    for ingredient in ingredients:
        _add_single_ingredient(shopping_list, ingredient, recipe, slot)

def _get_cleaned_ingredients(recipe):
    """ Get list of cleaned, non-empty ingredients from recipe. """
    raw_ingredients = recipe.ingredients.split('\n')
    return [ing.strip() for ing in raw_ingredients if ing.strip()]

def _add_single_ingredient(shopping_list, ingredient, recipe, slot):
    """ Add a single ingredient to shopping list. """
    category = categorise_ingredient(ingredient)
    shopping_list[category].append({
        'item': ingredient,
        'recipe': recipe.title,
        'day': slot.get_day_display(),
        'meal': slot.get_meal_type_display()
    })

def consolidate_ingredients(items):
    """ Group identical items and calculate quantities. """
    from recipes.helpers.recipe_detail_helpers import scale_ingredient
    consolidated = _build_consolidated_dict(items)
    return _format_consolidated_results(consolidated, scale_ingredient)

def _build_consolidated_dict(items):
    """ Build dictionary of consolidated ingredients. """
    consolidated = defaultdict(
        lambda: {'count': 0, 'recipes': [], 'base_item': None}
    )
    for item in items:
        _update_consolidated_entry(consolidated, item)
    return consolidated

def _update_consolidated_entry(consolidated, item):
    """ Update a single consolidated entry. """
    ingredient = item['item']
    key = ingredient.lower()
    
    if consolidated[key]['count'] == 0:
        consolidated[key]['base_item'] = ingredient
        
    consolidated[key]['count'] += 1
    recipe_info = f"{item['day']} {item['meal']}: {item['recipe']}"
    consolidated[key]['recipes'].append(recipe_info)

def _format_consolidated_results(consolidated, scale_ingredient):
    """ Format consolidated ingredients for display. """
    result = []
    
    for key, data in consolidated.items():
        formatted_item = _format_single_item(data, scale_ingredient)
        result.append(formatted_item)
    return result

def _format_single_item(data, scale_ingredient):
    """ Format a single consolidated item. """
    ingredient = data['base_item']
    count = data['count']
    
    if count > 1:
        return _create_scaled_item(ingredient, count, data, scale_ingredient)
    return _create_single_item(ingredient, data)

def _create_scaled_item(ingredient, count, data, scale_ingredient):
    """ Create a scaled item entry. """
    scaled = scale_ingredient(ingredient, count)
    return {
        'item': scaled,
        'count': count,
        'original': ingredient,
        'recipes': data['recipes']
    }

def _create_single_item(ingredient, data):
    """ Create a single item entry. """
    return {
        'item': ingredient,
        'count': 1,
        'original': ingredient,
        'recipes': data['recipes']
    }

def organise_shopping_list(shopping_list):
    """ Organise shopping list by category order. """
    organised = _consolidate_by_category(shopping_list)
    return _sort_by_category_order(organised)

def _consolidate_by_category(shopping_list):
    """ Consolidate items within each category. """
    organised = {}
    
    for category, items in shopping_list.items():
        organised[category] = consolidate_ingredients(items)
    return organised

def _sort_by_category_order(organised):
    """ Sort categories according to predefined order. """
    return [
        (category, organised[category])
        for category in CATEGORY_ORDER
        if category in organised
    ]