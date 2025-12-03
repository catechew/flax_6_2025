from django import forms
from django.contrib.auth import authenticate

class LogInForm(forms.Form):
    """ 
    Form enabling registered users to authenticate. 
    """
    
    username = forms.CharField(label="Username")
    password = forms.CharField(
        label="Password", 
        widget=forms.PasswordInput()
    )

    def get_user(self):
        """ Return authenticated user or None. """

        return authenticate(
            username=self.cleaned_data.get("username"),
            password=self.cleaned_data.get("password"),
        )