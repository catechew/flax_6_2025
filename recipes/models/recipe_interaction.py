from django.db import models

class RecipeInteractionMixin:
    """This Mixin class defines properties that all other models have. It removes the need to duplicate code in the admin.py file"""

    @property
    def recipe_title(self):
        """Get recipe title."""
        return self.recipe.title

    @property
    def recipe_author(self):
        """Get recipe author."""
        return self.recipe.author

    @property
    def recipe_rating(self):
        """Get recipe average rating."""
        return self.recipe.average_rating()