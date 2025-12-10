from django.test import TestCase
from datetime import date
from recipes.models import User, Recipe, Flag


class RecipeFlagCountTests(TestCase):
    """Test Recipe flag_count property."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='@testuser',
            email='test@example.com',
            password='Password123'
        )

        self.user2 = User.objects.create_user(
            username='@user2',
            email='user2@example.com',
            password='Password123'
        )

        self.recipe = Recipe.objects.create(
            author=self.user,
            title='Test Recipe',
            publication_date=date.today(),
            ingredients='Test (1)',
            steps='Test step',
        )

    def test_flag_count_zero(self):
        """Test flag_count returns 0 when no flags."""
        self.assertEqual(self.recipe.flag_count, 0)

    def test_flag_count_one(self):
        """Test flag_count returns 1 with one flag."""
        Flag.objects.create(recipe=self.recipe, user=self.user)
        self.assertEqual(self.recipe.flag_count, 1)

    def test_flag_count_multiple(self):
        """Test flag_count returns correct count with multiple flags."""
        Flag.objects.create(recipe=self.recipe, user=self.user)
        Flag.objects.create(recipe=self.recipe, user=self.user2)
        self.assertEqual(self.recipe.flag_count, 2)


class FlagModelTests(TestCase):
    """Test Flag model methods and properties."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='@testuser',
            email='test@example.com',
            password='Password123'
        )

        self.recipe = Recipe.objects.create(
            author=self.user,
            title='Test Recipe',
            publication_date=date.today(),
            ingredients='Test (1)',
            steps='Test step',
        )

        self.flag = Flag.objects.create(
            recipe=self.recipe,
            user=self.user
        )

    def test_flag_str_method(self):
        """Test Flag __str__ method."""
        expected = f"{self.user} flagged {self.recipe}."
        self.assertEqual(str(self.flag), expected)

    def test_flag_count_for_recipe_property(self):
        """Test flag_count_for_recipe property."""
        user2 = User.objects.create_user(
            username='@user2',
            email='user2@example.com',
            password='Password123'
        )
        Flag.objects.create(recipe=self.recipe, user=user2)
        self.assertEqual(self.flag.flag_count_for_recipe, 2)