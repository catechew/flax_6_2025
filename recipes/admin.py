from django.contrib import admin
from .models import User, Recipe, Rating, Flag, RecipeInteractionMixin


class RecipeInteractionAdmin(admin.ModelAdmin):
    """
    Base admin for Recipe interactions (Rating, Flag).
    """
    list_display = ("recipe_title", "recipe_author", "user", "recipe_rating")
    list_filter = ("recipe__author",)
    search_fields = ("recipe__title", "user__username", "recipe__author__username")
    readonly_fields = ("recipe_rating",)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "first_name", "last_name", "email", "gender")
    search_fields = ("username", "email", "first_name", "last_name")
    list_filter = ("gender", "avatar_type")


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "rating_display", "flag_count", "publication_date")
    search_fields = ("title", "author__username", "adjectives")
    list_filter = ("author", "publication_date")
    readonly_fields = ("rating_display", "flag_count", "adjectives")


@admin.register(Rating)
class RatingAdmin(RecipeInteractionAdmin):
    """
    Admin for recipe ratings.
    """
    list_display = RecipeInteractionAdmin.list_display + ("stars",)


@admin.register(Flag)
class FlagAdmin(RecipeInteractionAdmin):
    """ 
    Admin for recipe flags.
    """
    list_display = RecipeInteractionAdmin.list_display + ("flag_count_for_recipe",)
    readonly_fields = RecipeInteractionAdmin.readonly_fields + ("flag_count_for_recipe",)