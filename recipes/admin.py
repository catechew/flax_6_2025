from django.contrib import admin
from .models import User, Recipe, Rating

class UserAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "username", "email", "gender")

class RecipeAdmin(admin.ModelAdmin):
    list_display = ("average_rating", "author", "title", "adjectives", "ingredients", "steps", "image")

class RatingAdmin(admin.ModelAdmin):
    list_display = ("stars", "user", "recipe")

admin.site.register(User, UserAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Rating, RatingAdmin)