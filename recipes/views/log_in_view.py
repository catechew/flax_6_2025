from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.views import View

from recipes.forms import LogInForm
from recipes.views.decorators import LoginProhibitedMixin


class LogInView(LoginProhibitedMixin, View):
    """ 
    Display and process the login form. 
    """

    http_method_names = ['get', 'post']
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def get(self, request):
        self.next = request.GET.get("next") or ""
        return self.render()

    def post(self, request):
        self.next = request.POST.get("next") or ""
        form = LogInForm(request.POST)
        
        user = self._validate_and_get_user(form)
        if user is None:
            return self.render()
        login(request, user)
        redirect_url = self.next or self.redirect_when_logged_in_url
        return redirect(redirect_url)

    def _validate_and_get_user(self, form):
        """ Validate form and return user or None. """
        if not form.is_valid():
            messages.error(self.request, "The credentials provided were invalid!")
            return None
        
        user = form.get_user()
        if user is None:
            messages.error(self.request, "The credentials provided were invalid!")
        return user
    
    def render(self, form=None):
        return render(
            self.request,
            "auth/log_in.html",
            {
                "form": form or LogInForm(),
                "next": self.next,
            }
        )