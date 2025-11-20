from django.core.validators import MinLengthValidator, MinValueValidator
from django.conf import settings
from django.db import models


"""A Recipe can be posted by a user and later we will be able to do all CRUD operations on it.
    It has 5 fields as shown below"""

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

    image = models.ImageField(
        upload_to='recipe_images/',
        null=True,
        blank=True,
        help_text="Upload an image of the dish (optional)."
    )

    servings = models.PositiveIntegerField(
        default=4,
        validators=[MinValueValidator(1)],
        help_text="Number of servings this recipe makes"
    )

    ingredients = models.TextField(
        help_text="List ingredients, one per line (e.g., 'Garlic (5 cloves)')"
    )

    steps = models.TextField(
        help_text="List cooking steps, one per line"
    )


    class Meta: 
        ordering = ['-publication_date']  # Newest first
        
    def __str__(self):
        # Format ingredients and steps as multi-line text for readability
        ingredients_text = "\n".join(self.get_ingredient_list())
        steps_text = "\n".join(self.get_step_list())
        return (
            f"{self.author.username} ({self.publication_date.year}) \"{self.title}\" "
            f"Adjectives: {self.adjectives}.\n"
            f"Ingredients: {ingredients_text}\n"
            f"Steps: {steps_text}"
        )
    
    # Returns the ingredients as a list of lines
    def get_ingredient_list(self):
        return [line.strip() for line in self.ingredients.split('\n') if line.strip()]
    
    # Returns the steps as a list of lines
    def get_step_list(self):
        return [line.strip() for line in self.steps.split('\n') if line.strip()]