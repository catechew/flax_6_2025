from django.test import TestCase
from recipes.tests.utils import create_test_user, create_test_recipe
from recipes.models import User, Recipe, Rating

"""
Recipe rating behaviour tests.
"""


class RecipeModelRatingTests(TestCase):

    def setUp(self):
        self.user = create_test_user()
        self.recipe = create_test_recipe(author=self.user)

    def test_rating_count_initially_zero(self):
        self.assertEqual(self.recipe.rating_count(), 0)

    def test_average_rating_single(self):
        Rating.objects.create(recipe=self.recipe, user=self.user, stars=4)
        self.assertEqual(self.recipe.average_rating(), 4)

    def test_rating_str(self):
        """Test that the Rating model __str__ method returns the correct string."""
        rating = Rating.objects.create(recipe=self.recipe, user=self.user, stars=5)
        expected = f"{self.user} rated {self.recipe} - 5 stars"
        self.assertEqual(str(rating), expected)

    def test_rating_display_property(self):
        """Test rating_display property returns rounded average."""
        from recipes.models import Rating

        user2 = User.objects.create_user(
            username="@user2",
            email="user2@test.com",
            password="Password123",
            first_name="User",
            last_name="Two",
        )

        Rating.objects.create(recipe=self.recipe, user=self.user, stars=4)
        Rating.objects.create(recipe=self.recipe, user=user2, stars=5)

        self.assertEqual(self.recipe.rating_display, 4.5)

    def test_rating_display_with_no_ratings(self):
        """Test rating_display returns 0 when no ratings exist."""
        self.assertEqual(self.recipe.rating_display, 0.0)
