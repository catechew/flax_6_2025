from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from recipes.models import User


@login_required
def followers_list(request, user_id):
    """ Display list of users who follow this user. """
    profile_user = get_object_or_404(User, id=user_id)
    followers = profile_user.followers.all()

    return render(request, 'users/followers_list.html', {
        'profile_user': profile_user,
        'users': followers,
        'list_type': 'Followers',
    })

@login_required
def following_list(request, user_id):
    """ Display list of users this user follows. """
    profile_user = get_object_or_404(User, id=user_id)
    following = profile_user.following.all()

    return render(request, 'users/following_list.html', {
        'profile_user': profile_user,
        'users': following,
        'list_type': 'Following',
    })