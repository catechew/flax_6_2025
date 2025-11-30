from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Allow dict lookup in templates: dict[key]"""
    if not isinstance(dictionary, dict):
        return None
    return dictionary.get(key)


@register.filter
def get_slot(day_dict, meal_type):
    """Lookup nested dictionary day -> meal"""
    if not isinstance(day_dict, dict):
        return None
    return day_dict.get(meal_type)
