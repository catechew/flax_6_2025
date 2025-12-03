from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.views import View

from recipes.forms import LogInForm
from recipes.views.decorators import LoginProhibitedMixin


class LogInView(LoginProhibitedMixin, View):
    """ Display and process the login form. """

    http_method_names = ['get', 'post']
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def get(self, request):
        self.next = request.GET.get("next") or ""
        return self.render()

    def post(self, request):
        self.next = request.POST.get("next") or ""
        form = LogInForm(request.POST)

        if not form.is_valid():
            messages.error(request, "The credentials provided were invalid!")
            return self.render(form)

        user = form.get_user()
        if user is None:
            messages.error(request, "The credentials provided were invalid!")
            return self.render(form)

        login(request, user)
        redirect_url = self.next or self.redirect_when_logged_in_url
        return redirect(self.next)
    
    def render(self, form=None):
        return render(
            self.request,
            "auth/log_in.html",
            {
                "form": form or LogInForm(),
                "next": self.next,
            }
        )