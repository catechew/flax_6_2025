from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Q, Avg, Count
from recipes.models.recipe import Recipe

@login_required
def dashboard(request):
    """
    Display the current user's dashboard.

    This view renders the dashboard page for the authenticated user.
    It ensures that only logged-in users can access the page. 
    If a user is not authenticated, they are automatically redirected to the login
    page.
    """

    current_user = request.user
    # Get the 3 most recent recipes (public recipes + user's own private recipes)
    recent_recipes = Recipe.objects.visible_to(current_user).order_by('-publication_date')[:3]

    most_saved_recipes = (
        Recipe.objects.visible_to(current_user)
        .annotate(save_count=Count("saved_by"))
        .order_by("-save_count", "-publication_date")[:limit]
    )

    # Highest rated public recipes, ordered by average rating (descending)
    highest_rated_recipes = (
        Recipe.objects.visible()
        .annotate(avg_rating=Avg("ratings__stars"))
        .order_by("-avg_rating", "-publication_date")[:limit]
    )

    # Recipes from users being followed
    following_users = current_user.following.all()
    followed_recipes = (
        Recipe.objects.visible()
        .filter(author__in=following_users)
        .order_by('-publication_date')[:3]
    )

    context = {
        "user": user,
        "recent_recipes": get_recent_recipes(user),
        "most_saved_recipes": get_most_saved_recipes(),
        "highest_rated_recipes": get_highest_rated_recipes(),
        "followed_recipes": get_followed_recipes(user),
    }

    return render(request, "dashboard/dashboard.html", context)