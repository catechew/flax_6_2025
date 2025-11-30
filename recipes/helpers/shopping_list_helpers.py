""" Shopping list generation and categorisation. """

from collections import defaultdict

INGREDIENT_CATEGORIES = {
    '🥩 Meat & Poultry': ['chicken', 'beef'],
    
    '🐟 Seafood': ['salmon', 'tuna'],
    
    '🧀 Dairy & Eggs': ['cheese', 'cheddar', 'butter', 'milk', 'egg', 
                        'halloumi', 'tofu', 'bread'],
    
    '🥬 Vegetables': ['avocado', 'onion', 'garlic', 'tomatoes', 'lemon',
                      'spinach', 'ginger', 'broccoli', 'bell pepper', 'mushrooms'],

    '🍎 Fruits': ['apple', 'banana', 'lemon', 'strawberries'],
    
    '🌾 Grains & Pasta': ['rice', 'flour', 'penne', 'pasta', 'beans'],
    
    '🌶️ Spices & Herbs': ['black pepper', 'basil', 'leaves', 'cilantro', 'chili'],
    
    '🧂 Condiments': ['oil', 'sugar', 'sauce', 'soy', 'salt'],
}

CATEGORY_ORDER = [
    '🥬 Vegetables',
    '🍎 Fruits',
    '🥩 Meat & Poultry',
    '🐟 Seafood',
    '🧀 Dairy & Eggs',
    '🌾 Grains & Pasta',
    '🧂 Condiments',
    '🌶️ Spices & Herbs',
    '🛒 Other Items',
]

def categorise_ingredient(ingredient):
    """
    Categorise ingredient by type.
    
    Args:
        ingredient: Ingredient string
        
    Returns:
        str: Category emoji and name
    """
    ingredient_lower = ingredient.lower()
    
    for category, keywords in INGREDIENT_CATEGORIES.items():
        if _matches_category(ingredient_lower, keywords):
            return category
    
    return '🛒 Other Items'

def _matches_category(ingredient_lower, keywords):
    """ Check if ingredient matches any keyword. """
    return any(keyword in ingredient_lower for keyword in keywords)

def extract_ingredients(slots):
    """
    Extract all ingredients from meal slots.
    
    Args:
        slots: QuerySet of MealSlot objects
        
    Returns:
        dict: Ingredients grouped by category
    """
    shopping_list = defaultdict(list)
    
    for slot in slots:
        _add_recipe_ingredients(shopping_list, slot)
    
    return shopping_list

def _add_recipe_ingredients(shopping_list, slot):
    """ Add ingredients from a single recipe slot. """
    recipe = slot.recipe
    
    for ingredient in recipe.ingredients.split('\n'):
        ingredient = ingredient.strip()
        if ingredient:
            category = categorise_ingredient(ingredient)
            shopping_list[category].append({
                'item': ingredient,
                'recipe': recipe.title,
                'day': slot.get_day_display(),
                'meal': slot.get_meal_type_display()
            })

def consolidate_ingredients(items):
    """
    Group identical items and calculate quantities.
    
    Args:
        items: List of ingredient dicts
        
    Returns:
        list: Consolidated ingredients with counts
    """
    from recipes.views.recipe_detail_view import scale_ingredient
    
    consolidated = _build_consolidated_dict(items)
    return _format_consolidated_results(consolidated, scale_ingredient)

def _build_consolidated_dict(items):
    """ Build dictionary of consolidated ingredients. """
    consolidated = defaultdict(
        lambda: {'count': 0, 'recipes': [], 'base_item': None}
    )
    
    for item in items:
        ingredient = item['item']
        key = ingredient.lower()
        
        if consolidated[key]['base_item'] is None:
            consolidated[key]['base_item'] = ingredient
        
        consolidated[key]['count'] += 1
        recipe_info = f"{item['day']} {item['meal']}: {item['recipe']}"
        consolidated[key]['recipes'].append(recipe_info)
    
    return consolidated

def _format_consolidated_results(consolidated, scale_ingredient):
    """ Format consolidated ingredients for display. """
    result = []
    
    for key, data in consolidated.items():
        ingredient = data['base_item']
        count = data['count']
        
        if count > 1:
            scaled = scale_ingredient(ingredient, count)
            result.append({
                'item': scaled,
                'count': count,
                'original': ingredient,
                'recipes': data['recipes']
            })
        else:
            result.append({
                'item': ingredient,
                'count': 1,
                'original': ingredient,
                'recipes': data['recipes']
            })
    
    return result

def organise_shopping_list(shopping_list):
    """
    Organise shopping list by category order.
    
    Args:
        shopping_list: Dict of categorised ingredients
        
    Returns:
        list: Tuples of (category, items) in proper order
    """
    organised = {}
    
    for category, items in shopping_list.items():
        organised[category] = consolidate_ingredients(items)
    
    sorted_list = []
    for category in CATEGORY_ORDER:
        if category in organised:
            sorted_list.append((category, organised[category]))
    
    return sorted_list