from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Allow dict lookup in templates: dict[key]"""
    try:
        return dictionary.get(key)
    except:
        return None

@register.filter
def get_slot(day_dict, meal_type):
    """Lookup nested dictionary day → meal"""
    try:
        return day_dict.get(meal_type)
    except:
        return None
