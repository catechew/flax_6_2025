from django.test import TestCase
from django.urls import reverse
from recipes.models import Recipe, User
from recipes.tests.utils import get_default_user, create_test_recipes, create_test_users


class AllRecipesTabsTestCase(TestCase):
    """
    Tests for the all recipes view tabs functionality (recipes/users)
    """

    fixtures = [
        "recipes/tests/fixtures/default_user.json",
        "recipes/tests/fixtures/other_users.json",
    ]

    def setUp(self):
        self.user = get_default_user()
        self.url = reverse("all_recipes")
        self.client.login(username="@johndoe", password="Password123")
        self.recipe1 = create_test_recipes(count=3)

    def test_default_tab_is_recipes(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context["active_tab"], "recipes")

    def test_users_tab_parameter(self):
        response = self.client.get(self.url, {"tab": "users"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["active_tab"], "users")

    def test_recipes_tab_parameter(self):
        """Test explicitly accessing recipes tab."""
        response = self.client.get(self.url, {"tab": "recipes"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["active_tab"], "recipes")

    def test_search_users_by_username(self):
        response = self.client.get(self.url, {"q": "janedoe", "tab": "users"})
        self.assertEqual(response.status_code, 200)
        users = list(response.context["users"])

        jane = User.objects.get(username="@janedoe")
        self.assertIn(jane, users)

    def test_search_users_by_first_name(self):
        response = self.client.get(self.url, {"q": "Jane", "tab": "users"})
        users = list(response.context["users"])

        jane = User.objects.get(username="@janedoe")
        self.assertIn(jane, users)

    def test_search_users_by_last_name(self):
        response = self.client.get(self.url, {"q": "Pickles", "tab": "users"})
        users = list(response.context["users"])

        petra = User.objects.get(username="@petrapickles")
        self.assertIn(petra, users)

    def test_search_users_by_full_name(self):
        response = self.client.get(self.url, {"q": "Jane Doe", "tab": "users"})
        users = list(response.context["users"])

        jane = User.objects.get(username="@janedoe")
        self.assertIn(jane, users)

    def test_search_users_case_insensitive(self):
        response1 = self.client.get(self.url, {"q": "jane", "tab": "users"})
        response2 = self.client.get(self.url, {"q": "JANE", "tab": "users"})
        response3 = self.client.get(self.url, {"q": "JaNe", "tab": "users"})

        jane = User.objects.get(username="@janedoe")

        self.assertIn(jane, list(response1.context["users"]))
        self.assertIn(jane, list(response2.context["users"]))
        self.assertIn(jane, list(response3.context["users"]))

    def test_search_users_partial_match(self):
        """Test partial match in user search."""
        response = self.client.get(self.url, {"q": "doe", "tab": "users"})
        users = list(response.context["users"])

        jane = User.objects.get(username="@janedoe")
        john = User.objects.get(username="@johndoe")

        self.assertIn(jane, users)
        self.assertIn(john, users)

    def test_search_users_no_results(self):
        response = self.client.get(self.url, {"q": "NonExistentUser", "tab": "users"})
        users = list(response.context["users"])

        self.assertEqual(len(users), 0)
        self.assertEqual(response.context["page_object"].paginator.count, 0)

    def test_search_users_empty_query(self):
        """Test empty search on users tab returns all users."""
        response = self.client.get(self.url, {"q": "", "tab": "users"})
        users = list(response.context["users"])

        self.assertGreaterEqual(len(users), 3)

    def test_users_tab_context_variables(self):
        """Test that necessary context variables exist on users tab."""
        response = self.client.get(self.url, {"tab": "users"})

        self.assertIn("users", response.context)
        self.assertIn("page_object", response.context)
        self.assertIn("user_count", response.context)
        self.assertIn("recipe_count", response.context)
        self.assertIn("active_tab", response.context)
        self.assertIn("search_query", response.context)

    def test_recipe_count_in_users_tab(self):
        """Test that recipe count is available on users tab."""
        response = self.client.get(self.url, {"tab": "users"})

        self.assertIn("recipe_count", response.context)
        self.assertEqual(response.context["recipe_count"], 3)

    def test_user_count_in_recipes_tab(self):
        """Test that user count is available on recipes tab."""
        response = self.client.get(self.url, {"tab": "recipes"})

        self.assertIn("user_count", response.context)
        self.assertGreaterEqual(response.context["user_count"], 3)

    def test_users_tab_pagination_with_exactly_25_users(self):
        User.objects.exclude(id=self.user.id).delete()
        create_test_users(count=24)

        response = self.client.get(self.url, {"tab": "users"})
        self.assertEqual(response.context["page_object"].paginator.num_pages, 1)

    def test_users_tab_pagination_with_26_users(self):
        User.objects.exclude(id=self.user.id).delete()
        create_test_users(count=25)

        response = self.client.get(self.url, {"tab": "users"})
        self.assertEqual(response.context["page_object"].paginator.num_pages, 2)

    def test_users_tab_pagination_page_parameter(self):
        """Test that page parameter works on users tab."""
        User.objects.exclude(id=self.user.id).delete()
        create_test_users(count=30)

        response = self.client.get(self.url, {"tab": "users", "page": 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_object"].number, 2)
