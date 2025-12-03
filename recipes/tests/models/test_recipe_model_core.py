"""
Core Recipe model behaviour tests.
"""

from django.test import TestCase
from recipes.tests.utils import create_test_user, create_test_recipe

class RecipeModelCoreTests(TestCase):

    def setUp(self):
        self.user = create_test_user(username='@testuser')
        self.recipe = create_test_recipe(
            author=self.user,
            title="Korean Noodles",
            ingredients="Garlic (5 cloves)\nSoy sauce (2 tbsp)",
            steps="Mix\nFry",
        )

    def test_str_method(self):
        text = str(self.recipe)
        self.assertIn("Korean Noodles", text)
        self.assertIn("Garlic (5 cloves)", text)

    def test_get_ingredient_list(self):
        ingredients = self.recipe.get_ingredient_list()
        self.assertEqual(len(ingredients), 2)

    def test_get_step_list(self):
        steps = self.recipe.get_step_list()
        self.assertEqual(steps, ["Mix", "Fry"])