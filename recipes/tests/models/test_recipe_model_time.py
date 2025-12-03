"""
Recipe time calculation tests.
"""

from django.test import TestCase
from recipes.tests.utils import create_test_recipe

class RecipeModelTimeTests(TestCase):
    def setUp(self):
        self.recipe = create_test_recipe()

    def test_total_prep_minutes(self):
        self.recipe.prep_time_hours = 1
        self.recipe.prep_time_minutes = 30
        self.assertEqual(self.recipe.get_total_prep_time_minutes(), 90)

    def test_total_cook_minutes(self):
        self.recipe.cook_time_hours = 2
        self.recipe.cook_time_minutes = 15
        self.assertEqual(self.recipe.get_total_cook_time_minutes(), 135)

    def test_total_time_display(self):
        self.recipe.prep_time_minutes = 30
        self.recipe.cook_time_minutes = 30
        self.assertEqual(self.recipe.get_total_time_display(), "1 hr")
