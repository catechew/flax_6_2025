from django.test import TestCase
from recipes.tests.utils import create_test_user, create_test_recipe
from recipes.models import User, Recipe

"""
Recipe save tests.
"""


class RecipeModelSaveTests(TestCase):

    def setUp(self):
        self.user = create_test_user()
        self.recipe = create_test_recipe(author=self.user)

    def test_save_count_updates(self):
        self.assertEqual(self.recipe.get_save_count(), 0)
        self.recipe.saved_by.add(self.user)
        self.assertEqual(self.recipe.get_save_count(), 1)
