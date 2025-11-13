from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def all_recipes(request):
    """
    Display all recipes.
    """

    current_user = request.user
    return render(request, 'all_recipes.html', {'user': current_user})
