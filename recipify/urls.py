"""
URL configuration for recipify project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from recipes import views
from recipes.views.recipe_create_view import create_recipe, create_recipe_tags, cancel_recipe_creation

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('log_in/', views.LogInView.as_view(), name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('password/', views.PasswordView.as_view(), name='password'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),
    path('all_recipes/', views.all_recipes, name='all_recipes'),
    path('recipe/<int:recipe_id>', views.recipe_detail, name='recipe_detail'),
    path('update_recipe/<int:recipe_id>', views.recipe_update, name='update_recipe'),
    path('delete_recipe/<int:recipe_id>', views.recipe_delete, name='delete_recipe'),
    path('my_recipes/', views.my_recipes, name='my_recipes'),
    path('create_recipe/', create_recipe, name='create_recipe'),
    path('create_recipe/tags/', create_recipe_tags, name='create_recipe_tags'),
    path('create_recipe/cancel/', cancel_recipe_creation, name='cancel_recipe'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
