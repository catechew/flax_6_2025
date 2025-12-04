"""
Recipe save tests.
"""

from django.test import TestCase
from recipes.tests.utils import create_test_user, create_test_recipe

class RecipeModelSaveTests(TestCase):

    def setUp(self):
        self.user = create_test_user()
        self.recipe = create_test_recipe(author=self.user)

    def test_save_count_updates(self):
        self.assertEqual(self.recipe.get_save_count(), 0)
        self.recipe.saved_by.add(self.user)
        self.assertEqual(self.recipe.get_save_count(), 1)

    def test_flag_count_property(self):
        """Test flag_count property returns correct count."""
        from recipes.models import Flag

        user2 = User.objects.create_user(
            username='@user2',
            email='user2@test.com',
            password='Password123',
            first_name='User',
            last_name='Two'
        )

        Flag.objects.create(recipe=self.recipe, user=self.user)
        Flag.objects.create(recipe=self.recipe, user=user2)

        self.assertEqual(self.recipe.flag_count, 2)