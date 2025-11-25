from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
import uuid


@login_required
def randomise_avatar(request):
    """Generate a new random avatar seed for the user."""
    user = request.user

    # Clear uploaded picture if any
    if user.profile_picture:
        user.profile_picture.delete()
        user.profile_picture = None

    # Generate new random seed and set type
    user.avatar_seed = str(uuid.uuid4())
    user.avatar_type = 'random'
    user.save()

    messages.success(request, "Avatar randomised! Your new avatar is ready.")
    return redirect('profile')


@login_required
def use_initials_avatar(request):
    """Reset avatar to initials (default)."""
    user = request.user

    # Clear uploaded picture if any
    if user.profile_picture:
        user.profile_picture.delete()
        user.profile_picture = None

    # Clear random seed and set type to initials
    user.avatar_seed = ''
    user.avatar_type = 'initials'
    user.save()

    messages.success(request, "Avatar reset to initials!")
    return redirect('profile')