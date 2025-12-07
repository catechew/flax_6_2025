from django.test import TestCase
from recipes.models import User, Recipe, Rating
from datetime import date


class RecipeInteractionMixinTests(TestCase):
    """Test RecipeInteractionMixin properties."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='@testuser',
            email='test@example.com',
            password='Password123',
            first_name='Test',
            last_name='User'
        )

        self.recipe = Recipe.objects.create(
            author=self.user,
            title='Test Recipe',
            publication_date=date.today(),
            ingredients='Test (1)',
            steps='Test step',
        )

    def test_recipe_title_property(self):
        """Test recipe_title property."""
        rating = Rating.objects.create(
            recipe=self.recipe,
            user=self.user,
            stars=5
        )

        self.assertEqual(rating.recipe_title, 'Test Recipe')

    def test_recipe_author_property(self):
        """Test recipe_author property."""
        rating = Rating.objects.create(
            recipe=self.recipe,
            user=self.user,
            stars=5
        )

        self.assertEqual(rating.recipe_author, self.user)

    def test_recipe_rating_property(self):
        """Test recipe_rating property."""
        rating = Rating.objects.create(
            recipe=self.recipe,
            user=self.user,
            stars=4
        )

        self.assertEqual(rating.recipe_rating, 4.0)

