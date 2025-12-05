from django.core.validators import MinLengthValidator, MinValueValidator
from django.conf import settings
from django.db import models
from django.db.models import Avg
from .recipe_interaction import RecipeInteractionMixin
import math

class RecipeManager(models.Manager):
    def visible_to(self, user):
        """
        return recipes visible to a specific user (public + user's own)
        """
        if user.is_authenticated:
            return self.filter(
                models.Q(is_private=False) | models.Q(author=user)
            )
        return self.filter(is_private=False)
    
    def public(self):
        """
        return only public recipes
        """
        return self.filter(is_private=False)

class Recipe(models.Model):
    """
    A Recipe can be posted by a user and later we will be able to do all CRUD operations on it.
    """
    
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
    course_tags = models.TextField(
        blank=True,
        default='',
        help_text="Comma-separated course tags (e.g., 'main,dessert')"
    )
    dietary_tags = models.TextField(
        blank=True,
        default='',
        help_text="Comma-separated dietary tags (e.g., 'vegetarian,vegan')"
    )
    cuisine_tags = models.TextField(
        blank=True,
        default='',
        help_text="Comma-separated cuisine tags (e.g., 'Japanese, Asian, Chinese, Indian, Western, Jamaican')"
    )
    other_tags = models.TextField(
        blank=True,
        default='',
        help_text="Comma-separated other tags (e.g., 'high protein,low calorie')"
    )

    # Auto-populated combined tags field (for backward compatibility)
    adjectives = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text="Combined tags from all categories (auto-populated)"
    )

    publication_date = models.DateField()

    prep_time_hours = models.PositiveIntegerField(
        default=0,
        help_text="Preparation time in hours"
    )
    prep_time_minutes = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Preparation time in minutes"
    )
    cook_time_hours = models.PositiveIntegerField(
        default=0,
        help_text="Cooking time in hours"
    )
    cook_time_minutes = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Cooking time in minutes"
    )

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
        default="none",
        help_text="List ingredients, one per line (e.g., 'Garlic (5 cloves)')"
    )

    steps = models.TextField(
        default="none",
        help_text="List cooking steps, one per line"
    )

    private = models.BooleanField(
        default=False,
        help_text="Set this to true to hide the recipe from other users"
    )

    saved_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='saved_recipes',
        blank=True,
        help_text="Users who have saved this recipe"
    )

    def save(self, *args, **kwargs):
        """ Auto-populate adjectives from tag fields. """
        all_tags = []

        if self.course_tags:
            all_tags.extend([tag.strip() for tag in self.course_tags.split(',') if tag.strip()])
        if self.dietary_tags:
            all_tags.extend([tag.strip() for tag in self.dietary_tags.split(',') if tag.strip()])
        if self.cuisine_tags:
            all_tags.extend([tag.strip() for tag in self.cuisine_tags.split(',') if tag.strip()])
        if self.other_tags:
            all_tags.extend([tag.strip() for tag in self.other_tags.split(',') if tag.strip()])

        self.adjectives = ', '.join(all_tags) if all_tags else 'none'
        super().save(*args, **kwargs)

    class Meta: 
        ordering = ['-publication_date']  # Newest first
        
    def __str__(self):
        # Format ingredients and steps as multi-line text for readability. 
        ingredients_text = "\n".join(self.get_ingredient_list())
        steps_text = "\n".join(self.get_step_list())
        return (
            f"{self.author.username} ({self.publication_date.year}) \"{self.title}\" "
            f"Adjectives: {self.adjectives}.\n"
            f"Ingredients: {ingredients_text}\n"
            f"Steps: {steps_text}"
        )
    
    def get_ingredient_list(self):
        return [line.strip() for line in self.ingredients.split('\n') if line.strip()]
    
    def get_step_list(self):
        return [line.strip() for line in self.steps.split('\n') if line.strip()]
    
    def get_course_tags_list(self):
        return [tag.strip() for tag in self.course_tags.split(',') if tag.strip()]

    def get_dietary_tags_list(self):
        return [tag.strip() for tag in self.dietary_tags.split(',') if tag.strip()]
    
    def get_cuisine_tags_list(self):
        return [tag.strip() for tag in self.cuisine_tags.split(',') if tag.strip()]

    def get_other_tags_list(self):
        return [tag.strip() for tag in self.other_tags.split(',') if tag.strip()]

    def get_all_tags_list(self):
        return self.get_course_tags_list() + self.get_dietary_tags_list() + self.get_cuisine_tags_list() + self.get_other_tags_list()

    def get_total_prep_time_minutes(self):
        return (self.prep_time_hours * 60) + self.prep_time_minutes

    def get_total_cook_time_minutes(self):
        return (self.cook_time_hours * 60) + self.cook_time_minutes

    def format_time(self, hours, minutes):
        """ Format time as a readable strin. """
        if hours == 0 and minutes == 0:
            return "Not specified"
        parts = []
        if hours > 0:
            parts.append(f"{hours} hr" if hours == 1 else f"{hours} hrs")
        if minutes > 0:
            parts.append(f"{minutes} min")
        return " ".join(parts)

    def get_prep_time_display(self):
        return self.format_time(self.prep_time_hours, self.prep_time_minutes)

    def get_cook_time_display(self):
        return self.format_time(self.cook_time_hours, self.cook_time_minutes)
    
    def get_total_time_minutes(self):
        return self.get_total_cook_time_minutes() + self.get_total_prep_time_minutes()
    
    def get_total_time_display(self):
        total_minutes = self.get_total_time_minutes()
        total_hours = total_minutes // 60
        total_mins_remainder = total_minutes % 60

        if total_hours > 0 and total_mins_remainder > 0:
            return f"{total_hours} hr {total_mins_remainder} min" if total_hours == 1 else f"{total_hours} hrs {total_mins_remainder} min"
        elif total_hours > 0:
            return f"{total_hours} hr" if total_hours == 1 else f"{total_hours} hrs"
        elif total_mins_remainder > 0:
            return f"{total_mins_remainder} min"
        else:
            return None
        
    def get_save_count(self):
        return self.saved_by.count()

    def average_rating(self):
        return self.ratings.aggregate(avg=Avg("stars"))["avg"] or 0

    def average_rating_rounded(self):
        return math.floor(self.average_rating() + 0.5)

    def rating_count(self):
        """Return the number of ratings for this recipe"""
        return self.ratings.count()

    @property
    def rating_display(self):
        """Display average rating for admin."""
        return round(self.average_rating(), 2)

    @property
    def flag_count(self):
        """Total flags for this recipe."""
        return self.flags.count()
    
    objects = RecipeManager()
