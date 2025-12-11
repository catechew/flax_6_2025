"""
Tests for recipe flagging and unflagging views.
"""

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from recipes.models import Recipe, User
from recipes.models.flag import Flag


class FlagRecipeViewTestCase(TestCase):
    """
    Test suite for flag_recipe and unflag_recipe views.
    """

    fixtures = ["recipes/tests/fixtures/default_user.json"]

    def setUp(self):
        """Create user, recipe, and URLs used by all tests."""
        self.user = User.objects.get(username="@johndoe")
        self.client.login(username="@johndoe", password="Password123")

        self.recipe = Recipe.objects.create(
            author=self.user,
            title="Flaggable Recipe",
            publication_date=timezone.now().date(),
            ingredients="Test",
            steps="Test",
        )

        self.flag_url = reverse("flag_recipe", args=[self.recipe.id])
        self.unflag_url = reverse("unflag_recipe", args=[self.recipe.id])

    def test_flag_creates_new_flag(self):
        """Flagging a recipe creates exactly one flag."""
        response = self.client.post(self.flag_url)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Flag.objects.filter(recipe=self.recipe, user=self.user).exists()
        )

    def test_flagging_twice_does_not_duplicate(self):
        """Flagging a recipe twice does not create duplicates."""
        Flag.objects.create(recipe=self.recipe, user=self.user)

        response = self.client.post(self.flag_url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            Flag.objects.filter(recipe=self.recipe, user=self.user).count(), 1
        )

    def test_unflag_removes_existing_flag(self):
        """Unflagging removes an existing flag."""
        Flag.objects.create(recipe=self.recipe, user=self.user)

        response = self.client.post(self.unflag_url)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Flag.objects.filter(recipe=self.recipe, user=self.user).exists()
        )

    def test_unflag_without_existing_flag_is_safe(self):
        """Unflagging when no flag exists is handled safely."""
        response = self.client.post(self.unflag_url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Flag.objects.count(), 0)
