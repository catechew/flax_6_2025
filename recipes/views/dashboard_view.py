from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Q, Avg, Count
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
    # Get the 3 most recent recipes (public recipes + user's own private recipes)
    recent_recipes = Recipe.objects.filter(
        Q(private=False) | Q(author=current_user)
    ).order_by('-publication_date')[:3]

    # --- Most Saved Recipes (global) ---
    most_saved_recipes = (
        Recipe.objects.filter(private=False)
        .annotate(save_count=Count("saved_by"))
        .order_by("-save_count", "-publication_date")[:3]
    )

    # Highest rated public recipes, ordered by average rating (descending)
    highest_rated_recipes = (
        Recipe.objects.filter(private=False)
        .annotate(avg_rating=Avg("ratings__stars"))
        .order_by("-avg_rating", "-publication_date")[:3]
    )

    # Recipes from users being followed
    following_users = current_user.following.all()
    followed_recipes = (
        Recipe.objects.filter(
            private=False,
            author__in=following_users
        ).order_by('-publication_date')[:3]
    )

    context = {
        'user': current_user,
        'recent_recipes': recent_recipes,
        'most_saved_recipes': most_saved_recipes,
        "highest_rated_recipes": highest_rated_recipes,
        "followed_recipes": followed_recipes,
    }

    return render(request, 'dashboard/dashboard.html', context)
