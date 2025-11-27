from django.contrib import admin
from .models import User, Recipe

class UserAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "username", "email", "gender")

class RecipeAdmin(admin.ModelAdmin):
    list_display = ("author", "title", "adjectives", "ingredients", "steps", "image")

admin.site.register(User, UserAdmin)
admin.site.register(Recipe, RecipeAdmin)