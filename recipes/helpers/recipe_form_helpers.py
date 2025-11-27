"""
Helper functions for recipe create/update forms
"""

TAG_CATEGORIES = {
    'course' : ['dessert', 'main', 'appetiser', 'breakfast', 'snack'],
    'dietary' : ['vegetarian', 'vegan', 'halal', 'kosher', 'gluten-free', 'dairy-free'],
    'cuisine' : ['Japanese', 'Italian', 'Chinese', 'Asian', 'Persian', 'Jamaican', 'Western', 'British', 'Lebanese','Middle-Eastern'],
    'other' : ['high protein', 'low calorie', 'low carb', 'quick', 'budget']
}

def get_tag_action_from_request(request):
    """
    Parse POST request to determine tag action.
    Returns tuple: (action_type, category, value)

    action_type: 'add', 'remove', or None
    category: 'course', 'dietary', 'cuisine', 'other', or None
    value: tag value or None
    """

    if request.method != 'POST':
        return None, None, None
    
    # Check for add actions (predefined)
    for category in TAG_CATEGORIES.keys():
        field_name = f'add_{category}_tag'
        if field_name in request.POST:
            return 'add', category, request.POST.get(field_name)
        
    # Check for add actions (custom)
    for category in TAG_CATEGORIES.keys():
        field_name = f'add_{category}_tag_custom'
        if field_name in request.POST:
            value_field = f'{category}_tag_value'
            return 'add', category, request.POST.get(value_field)
    
    # Check for remove actions 
    for category in TAG_CATEGORIES.keys():
        field_name = f'remove_{category}_tag'
        if field_name in request.POST:
            return 'remove', category, request.POST.get(field_name)
    
    return None, None, None

