import os
from recipes.helpers.recipe_filter_options import (
 COURSE_OPTIONS,
 DIETARY_OPTIONS,
 CUISINE_OPTIONS,
 OTHER_OPTIONS,
)
from recipes.helpers.recipe_form_images import cleanup_temp_image

"""
Helper functions for recipe create/update forms
"""

TAG_CATEGORIES = {
    'course' : COURSE_OPTIONS,
    'dietary' : DIETARY_OPTIONS,
    'cuisine' : CUISINE_OPTIONS,
    'other' : OTHER_OPTIONS
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

def handle_tag_operation(session_data, action, category, value):
    """
    Add or remove a tag from session data.
    Returns True if operation was performed
    """

    if not action or not category or not value:
        return False
    
    # strip whitespace and limit length to 50
    value = value.strip()
    if not value or len(value) > 50:
        return False

    tag_key = f'{category}_tags'
    if tag_key not in session_data:
        session_data[tag_key] = []

    if action == 'add' and value not in session_data[tag_key]:
        session_data[tag_key].append(value)
        return True
    
    if action == 'remove' and value in session_data[tag_key]:
        session_data[tag_key].remove(value)
        return True
    
    return False

def get_tag_context(session_data):
    return {
        'course_tags' : session_data.get('course_tags', []),
        'dietary_tags': session_data.get('dietary_tags', []),
        'cuisine_tags': session_data.get('cuisine_tags', []),
        'other_tags': session_data.get('other_tags', []),
        'course_options': TAG_CATEGORIES['course'],
        'dietary_options': TAG_CATEGORIES['dietary'],
        'cuisine_options': TAG_CATEGORIES['cuisine'],
        'other_options': TAG_CATEGORIES['other'],
    }

def initialise_tag_session(session_data, recipe=None):
    """
    if recipe provided, populate from existing recipe tags.
    (For update recipe form)
    """

    if recipe:
        session_data['course_tags'] = recipe.get_course_tags_list()
        session_data['dietary_tags'] = recipe.get_dietary_tags_list()
        session_data['cuisine_tags'] = recipe.get_cuisine_tags_list()
        session_data['other_tags'] = recipe.get_other_tags_list()
    
    else:
        session_data['course_tags'] = []
        session_data['dietary_tags'] = []
        session_data['cuisine_tags'] = []
        session_data['other_tags'] = []

def apply_tags_to_recipe(recipe, session_data):
    """Apply tags from session data to recipe instance"""
    recipe.course_tags = ','.join(session_data.get('course_tags', []))
    recipe.dietary_tags = ','.join(session_data.get('dietary_tags', []))
    recipe.cuisine_tags = ','.join(session_data.get('cuisine_tags', []))
    recipe.other_tags = ','.join(session_data.get('other_tags', []))

def get_session_key(recipe_id=None):
    """ Generate session key for create or update mode. """
    return "recipe_form_data" if recipe_id is None else f"recipe_update_{recipe_id}"

def cleanup_session(session_key, session_data, request):
    """ Cleanup temporary files and session data. """
    cleanup_temp_image(session_data.get("temp_image_path"))

    if session_key in request.session:
        del request.session[session_key]

    request.session.modified = True
