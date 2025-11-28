from django.conf import settings
from django.db import models

"""
Flagging model allows a user to flag or report a recipe if it's inappropriate.
A user can flag a recipe once.
"""

class Flag(models.Model):
    recipe = models.ForeignKey(
        "recipes.Recipe",
        on_delete=models.CASCADE,
        related_name="flags",
        help_text="The recipe that was flagged"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="The user who flagged this recipe"
    )

    # Ensures each user can only flag a recipe once
    class Meta:
        unique_together = ("recipe", "user")

    def __str__(self):
        return f"{self.user} flagged {self.recipe}."