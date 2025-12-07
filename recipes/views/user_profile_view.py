from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from recipes.models import User, Recipe, Rating

@login_required
def user_profile(request, user_id):
    """ Display any user's profile (including your own). """
    profile_user = get_object_or_404(User, id=user_id)
    user_recipes = _get_user_recipes(request.user, profile_user)
    user_ratings = _get_user_ratings(profile_user)
    
    context = _build_profile_context(
        request.user, profile_user, user_recipes, user_ratings
    )
    return render(request, 'users/user_profile.html', context)

def _get_user_recipes(viewer, profile_user):
    """ Get recipes by profile user visible to viewer. """
    return Recipe.objects.visible_to(viewer).filter(
        author=profile_user
    ).order_by('-publication_date')

def _get_user_ratings(profile_user):
    """ Get all ratings by profile user. """
    return Rating.objects.filter(
        user=profile_user
    ).select_related('recipe', 'recipe__author')

def _build_profile_context(viewer, profile_user, recipes, ratings):
    """ Build context dictionary for profile template. """
    is_own_profile = viewer == profile_user
    is_following = viewer.is_following(profile_user) if not is_own_profile else False
    
    return {
        'profile_user': profile_user,
        'recipes': recipes,
        'recipe_count': recipes.count(),
        'user_ratings': ratings,
        'ratings_count': ratings.count(),
        'is_following': is_following,
        'is_own_profile': is_own_profile,
    }