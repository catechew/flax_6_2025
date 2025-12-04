from django.shortcuts import render
from recipes.views.decorators import login_prohibited

@login_prohibited
def home(request):
    return render(request, 'users/home.html')