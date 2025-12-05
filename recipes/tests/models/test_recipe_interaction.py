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

    def test_flag_count_for_recipe_property(self):
        """Test flag_count_for_recipe property on Flag model."""
        from recipes.models import Flag

        user2 = User.objects.create_user(
            username='@user2',
            email='user2@test.com',
            password='Password123',
            first_name='User',
            last_name='Two'
        )

        flag1 = Flag.objects.create(recipe=self.recipe, user=self.user)
        Flag.objects.create(recipe=self.recipe, user=user2)

        self.assertEqual(flag1.flag_count_for_recipe, 2)

    def test_flag_str_method(self):
        """Test Flag __str__ method."""
        from recipes.models import Flag

        flag = Flag.objects.create(recipe=self.recipe, user=self.user)
        expected = f"{self.user} flagged {self.recipe}."
        self.assertEqual(str(flag), expected)