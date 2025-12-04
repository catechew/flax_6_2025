from django.conf import settings
from django.db import models
from .recipe_interaction import RecipeInteractionMixin


class Flag(RecipeInteractionMixin, models.Model):
    """
    Flagging model allows a user to flag or report a recipe if it's inappropriate.
    A user can flag a recipe once.
    """

    recipe = models.ForeignKey(
        "Recipe",
        on_delete=models.CASCADE,
        related_name="flags",
        help_text="The recipe that was flagged"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='flags_created',
        help_text="The user who flagged this recipe"
    )

    class Meta:
        unique_together = ("recipe", "user")

    @property
    def flag_count_for_recipe(self):
        """Total flags for this recipe."""
        return self.recipe.flags.count()

    def __str__(self):
        return f"{self.user} flagged {self.recipe}."