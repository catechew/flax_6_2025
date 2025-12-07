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
    "course": COURSE_OPTIONS,
    "dietary": DIETARY_OPTIONS,
    "cuisine": CUISINE_OPTIONS,
    "other": OTHER_OPTIONS,
}

def get_tag_action_from_request(request):
    """ Parse POST request to determine tag action. """
    if request.method != "POST":
        return None, None, None

    results = [check_category_for_tag_action(request, cat) for cat in TAG_CATEGORIES]
    valid_results = [r for r in results if r != (None, None, None)]

    if not valid_results:
        return None, None, None
    return valid_results[0]

def check_category_for_tag_action(request, category):
    """ Check if a specific category has a tag action. """
    key = f"add_{category}_tag"
    if key in request.POST:
        return "add", category, request.POST.get(key)

    key = f"add_{category}_tag_custom"
    if key in request.POST:
        return "add", category, request.POST.get(f"{category}_tag_value")

    key = f"remove_{category}_tag"
    if key in request.POST:
        return "remove", category, request.POST.get(key)
    
    return None, None, None

def handle_tag_operation(session_data, action, category, value):
    """ Add or remove a tag from session data. """
    if not all([action, category, value]):
        return False

    value = value.strip()
    if not value or len(value) > 50:
        return False

    tag_key = f"{category}_tags"
    session_data.setdefault(tag_key, [])

    if action == "add":
        return _add_tag_to_list(session_data[tag_key], value)

    if action == "remove":
        return _remove_tag_from_list(session_data[tag_key], value)
    
    return False

def _add_tag_to_list(tag_list, value):
    """Add tag if not already present. Returns True (idempotent)."""
    if value not in tag_list:
        tag_list.append(value)
    return True

def _remove_tag_from_list(tag_list, value):
    """Remove tag if present."""
    if value in tag_list:
        tag_list.remove(value)
        return True
    return False

def get_tag_context(session_data):
    """ Build tag context for templates. """
    return {
        "course_tags": session_data.get("course_tags", []),
        "dietary_tags": session_data.get("dietary_tags", []),
        "cuisine_tags": session_data.get("cuisine_tags", []),
        "other_tags": session_data.get("other_tags", []),
        "course_options": TAG_CATEGORIES["course"],
        "dietary_options": TAG_CATEGORIES["dietary"],
        "cuisine_options": TAG_CATEGORIES["cuisine"],
        "other_options": TAG_CATEGORIES["other"],
    }

def initialise_tag_session(session_data, recipe=None):
    """ Initialise tags in session. """
    keys = ("course", "dietary", "cuisine", "other")
    for key in keys:
        session_data[f"{key}_tags"] = get_tag_list_for_key(recipe, key)

def get_tag_list_for_key(recipe, key):
    """Get tag list for a specific key from recipe or return empty list"""
    if recipe is None:
        return []
    return getattr(recipe, f"get_{key}_tags_list")()

def apply_tags_to_recipe(recipe, session_data):
    """ Apply tags from session to recipe. """
    recipe.course_tags = ",".join(session_data.get("course_tags", []))
    recipe.dietary_tags = ",".join(session_data.get("dietary_tags", []))
    recipe.cuisine_tags = ",".join(session_data.get("cuisine_tags", []))
    recipe.other_tags = ",".join(session_data.get("other_tags", []))

def get_session_key(recipe_id=None):
    """ Generate session key for recipe form. """
    return "recipe_form_data" if recipe_id is None else f"recipe_update_{recipe_id}"

def cleanup_session(session_key, session_data, request):
    """ Cleanup temp files and session data. """
    cleanup_temp_image(session_data.get("temp_image_path"))

    if session_key in request.session:
        del request.session[session_key]

    request.session.modified = True

def apply_ai_dietary_tags(session_data, ai_dietary_info):
    from recipes.helpers.ai_recipe_parser import map_ai_dietary_tags
    if not ai_dietary_info:
        return
    
    mapped_tags = map_ai_dietary_tags(ai_dietary_info)
    existing_tags = session_data.get('dietary_tags', [])
    
    # Add only new tags (no level 2 nesting)
    new_tags = [tag for tag in mapped_tags if tag not in existing_tags]
    existing_tags.extend(new_tags)
    session_data['dietary_tags'] = existing_tags

def get_ai_prefill_from_session(request):
    """ Get AI prefill data from session if available. """
    if not request.session.pop('from_ai_save_button', False):
        return None
    ai_data = request.session.pop('ai_recipe_prefill', None)
    return ai_data

def store_ai_dietary_info(session_data, ai_prefill):
    """ Store AI dietary info in session for tags page. """
    if 'ai_dietary_info' not in ai_prefill:
        return
    session_data['ai_dietary_info'] = ai_prefill.pop('ai_dietary_info')
    session_data['ai_description'] = ai_prefill.pop('ai_description', '')