from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
import uuid


@login_required
def randomize_avatar(request):
    """Generate a new random avatar seed for the user."""
    user = request.user

    if user.profile_picture:            # Clear uploaded picture if any
        user.profile_picture.delete()
        user.profile_picture = None

    # Generate new random seed
    user.avatar_seed = str(uuid.uuid4())
    user.save()

    messages.success(request, "Your new random avatar is ready!")
    return redirect('profile')