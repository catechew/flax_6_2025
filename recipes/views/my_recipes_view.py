from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from recipes.models import Recipe

@login_required
def my_recipes(request):

#Shows all user recipes under their profile, which also has their username, their Gravatar profile picture, and n. of their recipes

    user_recipes = Recipe.objects.filter(author=request.user)

    return render(request, 'my_recipes.html', {
        'user': request.user,
        'recipes': user_recipes,
        'recipe_count': user_recipes.count()
    })