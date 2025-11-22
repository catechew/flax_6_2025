from django.db import models
from django.conf import settings
from recipes.models.recipe import Recipe

class MealPlan(models.Model):
    """
    A weekly meal plan for a user.
    Each plan starts on a Monday (week_start).
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='meal_plans'
    )
    week_start = models.DateField()  # E.g. 2025-11-24 (Monday)

    class Meta: 
        """ User can only have one meal plan per week. """
        unique_together = ('user', 'week_start') 
    
    def __str__(self):
        return f"{self.user.username}'s plan for {self.week_start}"

class MealSlot(models.Model):
    """
    Represents a single meal slot (Breakfast, Lunch, Dinner, Snack) for a given day of the week.
    Eg: Tuesday - Dinner - Tuna Pasta
    """
    MEAL_TYPES = [
        ('breakfast', 'Breakfast'), 
        ('lunch', 'Lunch'), 
        ('dinner', 'Dinner'), 
        ('snack', 'Snack'), 
    ]

    DAYS = [
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
        ('sun', 'Sunday'),
    ]

    meal_plan = models.ForeignKey(
        MealPlan, 
        on_delete=models.CASCADE, 
        related_name='entries'
    )
    day=models.CharField(max_length=3, choices=DAYS)
    meal_type = models.CharField(max_length=10, choices=MEAL_TYPES)
    recipe = models.ForeignKey(
        Recipe,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    class Meta:
        unique_together = ('meal_plan', 'day', 'meal_type')
    
    def __str__(self):
        return f"{self.get_day_display()} - {self.get_meal_type_display()}"