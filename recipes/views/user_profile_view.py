from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from recipes.models import User, Recipe


@login_required
def user_profile(request, user_id):
    """Display any user's profile (including your own)."""
    profile_user = get_object_or_404(User, id=user_id)
    user_recipes = Recipe.objects.filter(author=profile_user).order_by('-publication_date')

    # Check if you're viewing your own profile or someone else's
    is_own_profile = request.user == profile_user
    is_following = request.user.is_following(profile_user) if not is_own_profile else False

    return render(request, 'user_profile.html', {
        'profile_user': profile_user,
        'recipes': user_recipes,
        'recipe_count': user_recipes.count(),
        'is_following': is_following,
        'is_own_profile': is_own_profile,
    })