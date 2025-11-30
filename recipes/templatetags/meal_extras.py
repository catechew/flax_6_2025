from django import template

register = template.Library()


@register.filter
def ordinal(n):
    """
    Adds suffix to dates eg: 21st November
    """
    n = int(n)

    # Special cases: 11th, 12th, 13th
    if 11 <= n % 100 <= 13:
        return f"{n}th"

    return f"{n}{ {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th') }"