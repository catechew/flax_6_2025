from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from recipes.models import Recipe
from django.shortcuts import redirect

@login_required
def my_recipes(request):
    """Redirect to current user's profile page."""
    return redirect('user_profile', user_id=request.user.id)