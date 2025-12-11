from django.test import TestCase
from django.urls import reverse
from recipes.models import Recipe, Rating, User
from recipes.tests.utils import get_default_user, create_test_recipe


class AllRecipesFilterTestCase(TestCase):
    """
    Tests for filter functionality in all recipes view.
    """

    fixtures = [
        "recipes/tests/fixtures/default_user.json",
        "recipes/tests/fixtures/other_users.json",
    ]

    def setUp(self):
        self.user = get_default_user()
        self.url = reverse("all_recipes")
        self.client.login(username="@johndoe", password="Password123")

    def test_filter_by_course_tag(self):
        """Test filtering recipes by course tag."""
        Recipe.objects.all().delete()
        breakfast_recipe = create_test_recipe(course_tags="breakfast")
        dinner_recipe = create_test_recipe(course_tags="main")
        response = self.client.get(self.url, {"course": "breakfast"})
        recipes = list(response.context["recipes"])

        self.assertEqual(response.status_code, 200)
        self.assertIn(breakfast_recipe, recipes)
        self.assertNotIn(dinner_recipe, recipes)

    def test_filter_by_dietary_tag(self):
        Recipe.objects.all().delete()
        vegan_recipe = create_test_recipe(dietary_tags="vegan")
        non_vegan_recipe = create_test_recipe(dietary_tags="")
        response = self.client.get(self.url, {"dietary": "vegan"})
        recipes = list(response.context["recipes"])

        self.assertEqual(response.status_code, 200)
        self.assertIn(vegan_recipe, recipes)
        self.assertNotIn(non_vegan_recipe, recipes)

    def test_filter_by_cuisine_tag(self):
        Recipe.objects.all().delete()
        italian_recipe = create_test_recipe(cuisine_tags="Italian")
        japanese_recipe = create_test_recipe(cuisine_tags="Japanese")
        response = self.client.get(self.url, {"cuisine": "Italian"})
        recipes = list(response.context["recipes"])

        self.assertEqual(response.status_code, 200)
        self.assertIn(italian_recipe, recipes)
        self.assertNotIn(japanese_recipe, recipes)

    def test_filter_by_other_tag(self):
        Recipe.objects.all().delete()
        quick_recipe = create_test_recipe(other_tags="quick")
        slow_recipe = create_test_recipe(other_tags="")
        response = self.client.get(self.url, {"other": "quick"})
        recipes = list(response.context["recipes"])
        self.assertEqual(response.status_code, 200)
        self.assertIn(quick_recipe, recipes)
        self.assertNotIn(slow_recipe, recipes)

    def test_filter_multiple_tags_same_category(self):
        Recipe.objects.all().delete()
        breakfast_recipe = create_test_recipe(course_tags="breakfast")
        dessert_recipe = create_test_recipe(course_tags="dessert")
        main_recipe = create_test_recipe(course_tags="main")
        response = self.client.get(self.url, {"course": ["breakfast", "dessert"]})
        recipes = list(response.context["recipes"])

        self.assertEqual(response.status_code, 200)
        self.assertIn(breakfast_recipe, recipes)
        self.assertIn(dessert_recipe, recipes)
        self.assertNotIn(main_recipe, recipes)

    def test_filter_context_variables(self):
        """Test that filter parameters are passed to context."""
        response = self.client.get(self.url, {"course": "main", "dietary": "vegan"})

        self.assertIn("filters", response.context)
        self.assertIn("course_filters", response.context["filters"])
        self.assertIn("dietary_filters", response.context["filters"])
        self.assertIn("main", response.context["filters"]["course_filters"])
        self.assertIn("vegan", response.context["filters"]["dietary_filters"])

    def test_filter_options_in_context(self):
        """Test that filter options are available in context."""
        response = self.client.get(self.url)

        self.assertIn("course_options", response.context)
        self.assertIn("dietary_options", response.context)
        self.assertIn("cuisine_options", response.context)
        self.assertIn("other_options", response.context)

    def test_sort_by_most_saved(self):
        """Test sorting recipes by most saved."""
        Recipe.objects.all().delete()

        recipe1 = create_test_recipe(title="Recipe 1")
        recipe2 = create_test_recipe(title="Recipe 2")

        user2 = User.objects.create_user(
            username="@user2", email="user2@example.com", password="Password123"
        )
        recipe1.saved_by.add(self.user)
        recipe1.saved_by.add(user2)
        recipe2.saved_by.add(self.user)

        response = self.client.get(self.url, {"sort": "most_saved"})
        recipes = list(response.context["recipes"])

        self.assertEqual(recipes[0], recipe1)
        self.assertEqual(recipes[1], recipe2)

    def test_sort_by_rating_highest(self):
        Recipe.objects.all().delete()

        recipe1 = create_test_recipe(title="Recipe 1")
        recipe2 = create_test_recipe(title="Recipe 2")
        user2 = User.objects.create_user(
            username="@user2", email="user2@example.com", password="Password123"
        )
        Rating.objects.create(recipe=recipe1, user=self.user, stars=5)
        Rating.objects.create(recipe=recipe2, user=user2, stars=3)

        response = self.client.get(self.url, {"sort": "rating_highest"})
        recipes = list(response.context["recipes"])

        self.assertEqual(recipes[0], recipe1)
        self.assertEqual(recipes[1], recipe2)
