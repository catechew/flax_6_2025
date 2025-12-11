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
    """

    model = User
    form_class = UserForm
    template_name = "users/profile.html"

    def get_object(self):
        """Return the authenticated user."""
        return self.request.user

    def form_valid(self, form):
        """Handle successful form submission."""
        response = super().form_valid(form)

        messages.add_message(
            self.request, messages.SUCCESS, "Profile updated successfully!"
        )
        return response

    def get_success_url(self):
        """Redirect user after successful profile update."""
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)
