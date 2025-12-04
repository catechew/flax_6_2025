from django.contrib import admin
from .models import User, Recipe, Rating, Flag


class UserAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "username", "email", "gender")


class RecipeAdmin(admin.ModelAdmin):
    list_display = ("average_rating", "author", "title", "adjectives", "ingredients", "steps", "image")


class RatingAdmin(admin.ModelAdmin):
    list_display = (
        "recipe_rating",
        "recipe_title",
        "recipe_author",
    )
    list_filter = ("recipe__author",)
    search_fields = ("recipe__title", "user__username", "recipe__author__username")

    def recipe_rating(self, obj):
        return obj.recipe.average_rating()

    recipe_rating.short_description = "Rating"
    def recipe_title(self, obj):
        return obj.recipe.title

    recipe_title.short_description = "Recipe Title"
    recipe_title.admin_order_field = "recipe__title"

    def recipe_author(self, obj):
        """ Show who created the recipe. """
        return obj.recipe.author

    recipe_author.short_description = "Recipe Author"
    recipe_author.admin_order_field = "recipe__author"


class FlagAdmin(admin.ModelAdmin):
    list_display = (
        "recipe_title",
        "recipe_author",
        "recipe_rating",
        "flag_count_for_recipe"
    )
    list_filter = ("recipe__author",)
    search_fields = ("recipe__title", "user__username", "recipe__author__username")

    def recipe_title(self, obj):
        """ Show the recipe title. """
        return obj.recipe.title

    recipe_title.short_description = "Recipe Title"
    recipe_title.admin_order_field = "recipe__title"

    def recipe_author(self, obj):
        """Show who created the recipe."""
        return obj.recipe.author

    recipe_author.short_description = "Recipe Author"
    recipe_author.admin_order_field = "recipe__author"

    def recipe_rating(self, obj):
        """ Show recipe rating. """
        return obj.recipe.average_rating()

    recipe_rating.short_description = "Rating"

    def flag_count_for_recipe(self, obj):
        """ Show total flags for this recipe. """
        return obj.recipe.flags.count()

    flag_count_for_recipe.short_description = "Total Flags"

admin.site.register(User, UserAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Rating, RatingAdmin)
admin.site.register(Flag, FlagAdmin)