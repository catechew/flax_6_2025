from django.conf import settings
from django.db import models
from .recipe_interaction import RecipeInteractionMixin


class Rating(RecipeInteractionMixin, models.Model):
    """
    Rating model allows authenticated users to leave a 1–5 star rating on a recipe.
    A user may only rate a recipe once.
    """

    recipe = models.ForeignKey(
        "Recipe",
        on_delete=models.CASCADE,
        related_name="ratings",
        help_text="The recipe this rating belongs to",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="The user who left this rating",
    )

    stars = models.PositiveSmallIntegerField(
        choices=[(i, i) for i in range(1, 6)], help_text="Rating value (1 to 5)"
    )

    class Meta:
        unique_together = ("recipe", "user")

    def __str__(self):
        return f"{self.user} rated {self.recipe} - {self.stars} stars"
