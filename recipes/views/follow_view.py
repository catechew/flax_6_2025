from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from recipes.models import User


@login_required
def follow_user(request, user_id):
    """ Follow a user. """
    user_to_follow = get_object_or_404(User, id=user_id)

    if user_to_follow == request.user:
        messages.error(request, "You can't follow yourself :(")
    elif request.user.is_following(user_to_follow):
        messages.info(request, f"You are already following {user_to_follow.get_full_name()}.")
    else:
        request.user.follow(user_to_follow)
        messages.success(request, f"You are now following {user_to_follow.get_full_name()}.")

    return redirect('user_profile', user_id=user_id)


@login_required
def unfollow_user(request, user_id):
    """ Unfollow a user. """
    user_to_unfollow = get_object_or_404(User, id=user_id)

    if not request.user.is_following(user_to_unfollow):
        messages.info(request, f"You are not following {user_to_unfollow.get_full_name()}.")
    else:
        request.user.unfollow(user_to_unfollow)
        messages.success(request, f"You unfollowed {user_to_unfollow.get_full_name()}.")

    return redirect('user_profile', user_id=user_id)