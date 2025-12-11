from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Q, Avg, Count
from recipes.models.recipe import Recipe


@login_required
def dashboard(request):
    """Display the current user's dashboard."""
    current_user = request.user

    recent_recipes = get_recent_recipes(current_user)
    most_saved_recipes = get_most_saved_recipes(current_user)
    highest_rated_recipes = get_highest_rated_recipes()
    followed_recipes = get_followed_recipes(current_user)

    context = build_dashboard_context(
        current_user,
        recent_recipes,
        most_saved_recipes,
        highest_rated_recipes,
        followed_recipes,
    )
    return render(request, "dashboard/dashboard.html", context)


def get_recent_recipes(user, limit=3):
    return Recipe.objects.visible_to(user).order_by("-publication_date")[:limit]


def get_most_saved_recipes(user, limit=3):
    return (
        Recipe.objects.visible_to(user)
        .annotate(save_count=Count("saved_by"))
        .order_by("-save_count", "-publication_date")[:limit]
    )


def get_highest_rated_recipes(limit=3):
    return (
        Recipe.objects.visible()
        .annotate(avg_rating=Avg("ratings__stars"))
        .order_by("-avg_rating", "-publication_date")[:limit]
    )


def get_followed_recipes(user, limit=3):
    """Get recent recipes from users being followed."""
    following_users = user.following.all()
    return (
        Recipe.objects.visible()
        .filter(author__in=following_users)
        .order_by("-publication_date")[:limit]
    )


def build_dashboard_context(user, recent, saved, rated, followed):
    """Build context dictionary for dashboard template."""
    return {
        "user": user,
        "recent_recipes": recent,
        "most_saved_recipes": saved,
        "highest_rated_recipes": rated,
        "followed_recipes": followed,
    }
