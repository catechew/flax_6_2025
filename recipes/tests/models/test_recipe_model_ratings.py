"""
Recipe rating behaviour tests.
"""

from django.test import TestCase
from recipes.models.rating import Rating
from recipes.tests.utils import create_test_user, create_test_recipe

class RecipeModelRatingTests(TestCase):

    def setUp(self):
        self.user = create_test_user()
        self.recipe = create_test_recipe(author=self.user)

    def test_rating_count_initially_zero(self):
        self.assertEqual(self.recipe.rating_count(), 0)

    def test_average_rating_single(self):
        Rating.objects.create(recipe=self.recipe,
                              user=self.user, stars=4)
        self.assertEqual(self.recipe.average_rating(), 4)
