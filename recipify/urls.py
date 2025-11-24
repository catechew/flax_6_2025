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

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from recipes.views.home_view import home
from recipes.views.dashboard_view import dashboard

from recipes.views.log_in_view import LogInView
from recipes.views.log_out_view import log_out
from recipes.views.password_view import PasswordView
from recipes.views.profile_view import ProfileUpdateView
from recipes.views.sign_up_view import SignUpView

from recipes.views.all_recipes_view import all_recipes
from recipes.views.recipe_detail_view import recipe_detail
from recipes.views.recipe_delete_view import recipe_delete
from recipes.views.my_recipes_view import my_recipes

from recipes.views.follow_view import follow_user, unfollow_user
from recipes.views.user_profile_view import user_profile
from recipes.views.followers_list_view import followers_list, following_list

from recipes.views.saved_recipe_view import toggle_save_recipe, saved_recipe_list

from recipes.views.rating_view import rate_recipe

from recipes.views.recipe_create_view import (
    create_recipe,
    create_recipe_tags,
    cancel_recipe_creation
)

from recipes.views.recipe_update_view import (
    recipe_update,
    update_recipe_tags,
    cancel_recipe_update
)

# Meal plan views
from recipes.views.meal_plan_view import (
    MealPlanCreateView,
    MealPlanDetailView,
    MealSlotUpdateView,
    MealPlanNavigateView,
    MealSlotClearView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),

    path('log_in/', LogInView.as_view(), name='log_in'),
    path('log_out/', log_out, name='log_out'),
    path('password/', PasswordView.as_view(), name='password'),
    path('profile/', ProfileUpdateView.as_view(), name='profile'),
    path('sign_up/', SignUpView.as_view(), name='sign_up'),

    path('all_recipes/', all_recipes, name='all_recipes'),
    path('recipe/<int:recipe_id>', recipe_detail, name='recipe_detail'),
    path('delete_recipe/<int:recipe_id>', recipe_delete, name='delete_recipe'),
    path('my_recipes/', my_recipes, name='my_recipes'),

    path('create_recipe/', create_recipe, name='create_recipe'),
    path('create_recipe/tags/', create_recipe_tags, name='create_recipe_tags'),
    path('create_recipe/cancel/', cancel_recipe_creation, name='cancel_recipe'),

    path('update_recipe/<int:recipe_id>', recipe_update, name='update_recipe'),
    path('update_recipe/<int:recipe_id>/tags/', update_recipe_tags, name='update_recipe_tags'),
    path('update_recipe/<int:recipe_id>/cancel/', cancel_recipe_update, name='cancel_recipe_update'),

    path('user/<int:user_id>/', user_profile, name='user_profile'),
    path('user/<int:user_id>/follow/', follow_user, name='follow_user'),
    path('user/<int:user_id>/unfollow/', unfollow_user, name='unfollow_user'),
    path('user/<int:user_id>/followers/', followers_list, name='followers_list'),
    path('user/<int:user_id>/following/', following_list, name='following_list'),

    path('meal-plan/create/', MealPlanCreateView.as_view(), name='meal-plan-create'),
    path('meal-plan/<int:plan_id>/', MealPlanDetailView.as_view(), name='meal-plan-detail'),
    path('meal-slot/<int:slot_id>/update/', MealSlotUpdateView.as_view(), name='meal-slot-update'),
    path("meal-plan/<int:plan_id>/<str:direction>/", MealPlanNavigateView.as_view(), name="meal-plan-navigate"),
    path("meal-slot/<int:slot_id>/clear/", MealSlotClearView.as_view(), name="meal-slot-clear"),

    path('recipe/<int:recipe_id>/save/', toggle_save_recipe, name='toggle_save_recipe'),
    path('saved_recipes/', saved_recipe_list, name='saved_recipe_list'),

    path("recipes/<int:recipe_id>/rate/", rate_recipe, name="rate_recipe"),
] 

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)