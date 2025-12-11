from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from recipes.models import User, Recipe
from recipes.models.rating import Rating

"""
Tests for the star rating feature.
"""


class RatingViewTestCase(TestCase):
    """
    Tests for rating a recipe via the rate_recipe view.
    """

    fixtures = ["recipes/tests/fixtures/default_user.json"]

    def setUp(self):
        """Set up a test user and a recipe."""
        self.user = User.objects.get(username="@johndoe")
        self.other_user = User.objects.create_user(
            username="@janedoe", email="jane@example.org", password="Password123"
        )
        self.recipe = Recipe.objects.create(
            author=self.user,
            title="Temp Recipe",
            publication_date=timezone.now().date(),
            ingredients="Garlic (1)",
            steps="Cook",
        )
        self.url = reverse("rate_recipe", kwargs={"recipe_id": self.recipe.id})

    def test_rate_recipe_url(self):
        """Test that the rate_recipe URL is correct."""
        self.assertEqual(self.url, f"/recipes/{self.recipe.id}/rate/")

    def test_rating_requires_login(self):
        """Test that an unauthenticated user is redirected to login."""
        response = self.client.post(self.url)
        login_url = reverse("log_in")
        self.assertRedirects(response, f"{login_url}?next={self.url}")

    def test_user_can_rate_recipe(self):
        """Test that a logged-in user can submit a rating."""
        self.client.login(username="@janedoe", password="Password123")
        response = self.client.post(self.url, {"stars": 4}, follow=True)
        rating_exists = Rating.objects.filter(
            recipe=self.recipe, user=self.other_user, stars=4
        ).exists()
        self.assertTrue(rating_exists)
        detail_url = reverse("recipe_detail", kwargs={"recipe_id": self.recipe.id})
        self.assertRedirects(
            response, detail_url, status_code=302, target_status_code=200
        )

    def test_user_can_update_rating(self):
        """Test that rating an already-rated recipe updates the rating."""
        self.client.login(username="@janedoe", password="Password123")
        Rating.objects.create(recipe=self.recipe, user=self.other_user, stars=2)
        self.client.post(self.url, {"stars": 5})
        updated_rating = Rating.objects.get(recipe=self.recipe, user=self.other_user)
        self.assertEqual(updated_rating.stars, 5)

    def test_cannot_rate_own_recipe(self):
        """Test that recipe authors cannot rate their own recipe."""
        self.client.login(username="@johndoe", password="Password123")
        response = self.client.post(self.url, {"stars": 5}, follow=True)
        self.assertFalse(
            Rating.objects.filter(recipe=self.recipe, user=self.user).exists()
        )
        detail_url = reverse("recipe_detail", kwargs={"recipe_id": self.recipe.id})
        self.assertRedirects(response, detail_url)
        messages = list(response.context["messages"])
        self.assertTrue(
            any("You cannot rate your own recipe." in str(m) for m in messages)
        )

    def test_invalid_rating_ignored(self):
        """Test that invalid star values do not create a rating."""
        self.client.login(username="@janedoe", password="Password123")
        self.client.post(self.url, {"stars": 0})
        self.assertFalse(
            Rating.objects.filter(recipe=self.recipe, user=self.other_user).exists()
        )
        self.client.post(self.url, {"stars": 6})
        self.assertFalse(
            Rating.objects.filter(recipe=self.recipe, user=self.other_user).exists()
        )

    def test_average_rating_and_count(self):
        """Test that average rating and rating_count work correctly."""
        Rating.objects.create(recipe=self.recipe, user=self.other_user, stars=4)
        Rating.objects.create(recipe=self.recipe, user=self.user, stars=3)
        self.assertEqual(self.recipe.rating_count(), 2)
        self.assertAlmostEqual(self.recipe.average_rating(), 3.5)
        self.assertEqual(self.recipe.average_rating_rounded(), 4)

    def test_get_request_does_not_create_rating(self):
        """Test that a GET request does not process a rating."""
        self.client.login(username="@janedoe", password="Password123")
        response = self.client.get(self.url)
        self.assertFalse(
            Rating.objects.filter(recipe=self.recipe, user=self.other_user).exists()
        )
        detail_url = reverse("recipe_detail", kwargs={"recipe_id": self.recipe.id})
        self.assertRedirects(response, detail_url)
