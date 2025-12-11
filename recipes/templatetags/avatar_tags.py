from django import template

register = template.Library()


@register.simple_tag
def get_avatar_url(user, size=120):
    """Get avatar URL for a user with specified size."""
    return user.avatar_url(size=size)
