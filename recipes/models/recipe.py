from django.core.validators import MinLengthValidator
from django.conf import settings
from django.db import models

"""A Recipe can be posted by a user and later we will be able to do all CRUD operations on it.
    It has 4 fields as shown below"""

class Recipe(models.Model):
    
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='recipes',
        help_text="The user who created this recipe"
    )
    title = models.CharField(
        max_length=255,
        validators=[MinLengthValidator(4)]
    )
    adjectives = models.CharField(
        max_length=255,
        validators=[MinLengthValidator(4)],
        help_text="Descriptive words for the recipe (e.g., 'quick', 'healthy', 'cheap')"
    )
    publication_date = models.DateField()

    class Meta: 
        ordering = ['-publication_date']  # Newest first
        
    def __str__(self):
        return f"{self.author.username} ({self.publication_date.year}) \"{self.title}\" Adjectives: {self.adjectives}."