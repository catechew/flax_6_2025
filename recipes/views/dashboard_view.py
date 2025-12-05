"""
    Display the current user's dashboard.

    This view renders the dashboard page for the authenticated user.
    It ensures that only logged-in users can access the page. 
    If a user is not authenticated, they are automatically redirected to the login
    page.
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Q, Avg, Count
from recipes.models.recipe import Recipe

def get_recent_recipes(user, limit=3):
    return (
        Recipe.objects.filter(Q(private=False) | Q(author=user))
        .order_by("-publication_date")[:limit]
    )

def get_most_saved_recipes(limit=3):
    return (
        Recipe.objects.filter(private=False)
        .annotate(save_count=Count("saved_by"))
        .order_by("-save_count", "-publication_date")[:limit]
    )

def get_highest_rated_recipes(limit=3):
    return (
        Recipe.objects.filter(private=False)
        .annotate(avg_rating=Avg("ratings__stars"))
        .order_by("-avg_rating", "-publication_date")[:limit]
    )

def get_followed_recipes(user, limit=3):
    following = user.following.all()
    return (
        Recipe.objects.filter(private=False, author__in=following)
        .order_by("-publication_date")[:limit]
    )

@login_required
def dashboard(request):
    user = request.user

    context = {
        "user": user,
        "recent_recipes": get_recent_recipes(user),
        "most_saved_recipes": get_most_saved_recipes(),
        "highest_rated_recipes": get_highest_rated_recipes(),
        "followed_recipes": get_followed_recipes(user),
    }

    return render(request, "dashboard/dashboard.html", context)