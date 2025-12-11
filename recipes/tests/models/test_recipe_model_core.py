from django.test import TestCase
from django.contrib.auth.models import AnonymousUser
from recipes.models import User, Recipe, Flag
from datetime import date


class RecipeManagerTests(TestCase):
    """
    Test Recipe manager methods.
    """

    def setUp(self):
        """Set up test data."""
        self._create_users()
        self._create_recipes()

    def _create_users(self):
        """Create test users."""
        self.user = User.objects.create_user(
            username="@testuser", email="test@example.com", password="Password123"
        )
        self.other_user = User.objects.create_user(
            username="@otheruser", email="other@example.com", password="Password123"
        )

    def _create_recipes(self):
        """Create test recipes (public and private)."""
        self.public_recipe = Recipe.objects.create(
            author=self.user,
            title="Public Recipe",
            publication_date=date.today(),
            ingredients="Test (1)",
            steps="Test step",
            private=False,
        )
        self.private_recipe = Recipe.objects.create(
            author=self.user,
            title="Private Recipe",
            publication_date=date.today(),
            ingredients="Test (1)",
            steps="Test step",
            private=True,
        )

    def test_visible_to_authenticated_user_sees_own_private(self):
        """Authenticated user sees their own private recipes."""
        recipes = Recipe.objects.visible_to(self.user)

        self.assertIn(self.public_recipe, recipes)
        self.assertIn(self.private_recipe, recipes)

    def test_visible_to_authenticated_user_not_see_others_private(self):
        """Authenticated user doesn't see other users' private recipes."""
        recipes = Recipe.objects.visible_to(self.other_user)

        self.assertIn(self.public_recipe, recipes)
        self.assertNotIn(self.private_recipe, recipes)

    def test_visible_to_unauthenticated_user(self):
        """Unauthenticated user only sees public recipes."""
        anon_user = AnonymousUser()
        recipes = Recipe.objects.visible_to(anon_user)

        self.assertIn(self.public_recipe, recipes)
        self.assertNotIn(self.private_recipe, recipes)

    def test_visible_method(self):
        """Visible() returns only public recipes."""
        recipes = Recipe.objects.visible()

        self.assertIn(self.public_recipe, recipes)
        self.assertNotIn(self.private_recipe, recipes)

    def test_public_method(self):
        """Public() returns only public recipes."""
        recipes = Recipe.objects.public()

        self.assertIn(self.public_recipe, recipes)
        self.assertNotIn(self.private_recipe, recipes)
