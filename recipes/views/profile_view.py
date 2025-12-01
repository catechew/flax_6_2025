from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic.edit import UpdateView

from recipes.forms import UserForm


User = get_user_model()


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
    Allow authenticated users to view and update their profile information.

    This class-based view displays a user profile editing form and handles
    updates to the authenticated user’s profile. Access is restricted to
    logged-in users via `LoginRequiredMixin`.
    """

    model = User
    form_class = UserForm
    template_name = "users/profile.html"

    def get_object(self):
        """
        Return the authenticated user.

        Ensures users can only update their own profile.
        """
        return self.request.user

    def get_success_url(self):
        """
        Redirect user after successful profile update.
        """
        messages.add_message(self.request, messages.SUCCESS, "Profile updated!")
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)