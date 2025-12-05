"""
Recipe flag tests.
"""

from django.test import TestCase
from recipes.tests.utils import create_test_user, create_test_recipe
from recipes.models import User, Recipe, Flag


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


def test_recipe_flag_count_zero(self):
    """Test flag_count returns 0 when no flags."""
    self.assertEqual(self.recipe.flag_count, 0)


def test_recipe_flag_count_multiple(self):
    """Test flag_count returns correct count."""
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