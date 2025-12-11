from django.test import TestCase, Client
from django.urls import reverse
from recipes.models import User, Recipe, Rating
from datetime import date, timedelta


class DashboardViewTests(TestCase):
    """Test dashboard view functionality."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self._create_users()
        self._create_user_recipes()
        self._create_other_user_recipes()
        self.url = reverse("dashboard")

    def _create_users(self):
        """Create test users."""
        self.user = User.objects.create_user(
            username="@testuser",
            email="test@example.com",
            password="Password123",
            first_name="Test",
            last_name="User",
        )
        self.other_user = User.objects.create_user(
            username="@otheruser",
            email="other@example.com",
            password="Password123",
            first_name="Other",
            last_name="User",
        )
        self.followed_user = User.objects.create_user(
            username="@followed",
            email="followed@example.com",
            password="Password123",
            first_name="Followed",
            last_name="User",
        )
        self.user.follow(self.followed_user)

    def _create_user_recipes(self):
        """Create recipes for main test user."""
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
            publication_date=date.today() - timedelta(days=1),
            ingredients="Test (1)",
            steps="Test step",
            private=True,
        )

    def _create_other_user_recipes(self):
        """Create recipes for other users."""
        self.other_recipe = Recipe.objects.create(
            author=self.other_user,
            title="Other User Recipe",
            publication_date=date.today() - timedelta(days=2),
            ingredients="Test (1)",
            steps="Test step",
            private=False,
        )
        self.followed_recipe = Recipe.objects.create(
            author=self.followed_user,
            title="Followed User Recipe",
            publication_date=date.today(),
            ingredients="Test (1)",
            steps="Test step",
            private=False,
        )

    def test_requires_login(self):
        """Dashboard requires authentication."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/log_in/", response.url)

    def test_authenticated_user_can_access(self):
        """Authenticated user can access dashboard."""
        self.client.login(username="@testuser", password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard/dashboard.html")

    def test_shows_most_saved_recipes(self):
        """Dashboard shows most saved recipes."""
        self.public_recipe.saved_by.add(self.user)
        self.public_recipe.saved_by.add(self.other_user)
        self.other_recipe.saved_by.add(self.user)
        self.client.login(username="@testuser", password="Password123")
        response = self.client.get(self.url)
        most_saved = response.context["most_saved_recipes"]
        self.assertGreater(len(most_saved), 0)
        self.assertEqual(most_saved[0], self.public_recipe)

    def test_shows_highest_rated_recipes(self):
        """Dashboard shows highest rated recipes."""
        Rating.objects.create(recipe=self.public_recipe, user=self.user, stars=5)
        Rating.objects.create(recipe=self.other_recipe, user=self.user, stars=3)
        self.client.login(username="@testuser", password="Password123")
        response = self.client.get(self.url)
        highest_rated = response.context["highest_rated_recipes"]
        self.assertGreater(len(highest_rated), 0)
        self.assertEqual(highest_rated[0], self.public_recipe)

    def test_shows_followed_user_recipes(self):
        """Dashboard shows recipes from followed users."""
        self.client.login(username="@testuser", password="Password123")
        response = self.client.get(self.url)
        followed_recipes = response.context["followed_recipes"]
        self.assertIn(self.followed_recipe, followed_recipes)
        self.assertNotIn(self.other_recipe, followed_recipes)

    def test_does_not_show_private_recipes_from_others(self):
        """Dashboard does not show private recipes from other users."""
        private_other = Recipe.objects.create(
            author=self.other_user,
            title="Private Other Recipe",
            publication_date=date.today(),
            ingredients="Test (1)",
            steps="Test step",
            private=True,
        )
        self.client.login(username="@testuser", password="Password123")
        response = self.client.get(self.url)
        recent_recipes = response.context["recent_recipes"]

        self.assertNotIn(private_other, recent_recipes)

    def test_limits_to_three_recipes_each(self):
        """Each section shows max 3 recipes."""
        for i in range(5):
            Recipe.objects.create(
                author=self.user,
                title=f"Recipe {i}",
                publication_date=date.today() - timedelta(days=i),
                ingredients="Test (1)",
                steps="Test step",
                private=False,
            )
        self.client.login(username="@testuser", password="Password123")
        response = self.client.get(self.url)

        self.assertEqual(len(response.context["recent_recipes"]), 3)

    def test_context_has_all_required_keys(self):
        """Context contains all required data."""
        self.client.login(username="@testuser", password="Password123")
        response = self.client.get(self.url)

        self.assertIn("user", response.context)
        self.assertIn("recent_recipes", response.context)
        self.assertIn("most_saved_recipes", response.context)
        self.assertIn("highest_rated_recipes", response.context)
        self.assertIn("followed_recipes", response.context)

    def test_user_context_is_current_user(self):
        """User in context is the logged-in user."""
        self.client.login(username="@testuser", password="Password123")
        response = self.client.get(self.url)

        self.assertEqual(response.context["user"], self.user)

    def test_empty_followed_list(self):
        """Dashboard works when user follows nobody."""
        lonely_user = User.objects.create_user(
            username="@lonely",
            email="lonely@example.com",
            password="Password123",
            first_name="Lonely",
            last_name="User",
        )
        self.client.login(username="@lonely", password="Password123")
        response = self.client.get(self.url)
        followed_recipes = response.context["followed_recipes"]
        self.assertEqual(len(followed_recipes), 0)

    def test_no_ratings_exist(self):
        """Dashboard works when no ratings exist."""
        self.client.login(username="@testuser", password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
