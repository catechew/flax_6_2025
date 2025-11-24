from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from recipes.models.recipe import Recipe

@login_required
def dashboard(request):
    """
    Display the current user's dashboard.

    This view renders the dashboard page for the authenticated user.
    It ensures that only logged-in users can access the page. If a user
    is not authenticated, they are automatically redirected to the login
    page.
    """

    current_user = request.user
    # Get the 3 most recent recipes, order by publication_date descending, limit to 3
    recent_recipes = Recipe.objects.order_by('-publication_date')[:3]

    # Get the user's saved recipes, limit to 3
    saved_recipes = current_user.saved_recipes.all().order_by('-publication_date')[:3]

    context = {
        'user': current_user,
        'recent_recipes': recent_recipes,
        'saved_recipes': saved_recipes,
    }

    return render(request, 'dashboard.html', context)
