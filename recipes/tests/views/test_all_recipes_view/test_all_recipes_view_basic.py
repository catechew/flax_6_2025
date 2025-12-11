from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from recipes.models import Recipe
from recipes.tests.utils import (
    create_test_recipes,
    get_default_user,
    create_test_recipe,
)


class AllRecipesBasicViewTestCase(TestCase):
    """tests for basic all recipes view functionality"""

    fixtures = [
        "recipes/tests/fixtures/default_user.json",
        "recipes/tests/fixtures/other_users.json",
    ]

    def setUp(self):
        self.user = get_default_user()
        self.url = reverse("all_recipes")
        self.client.login(username="@johndoe", password="Password123")

        self.recipe1 = create_test_recipe(
            title="Overnight Oats",
            ingredients="Oats (1 cup)\nGreek Yoghurt (300g)",
            steps="Mix ingredients together\nPut it in the fridge overnight",
            other_tags="healthy",
        )

        self.recipe2 = create_test_recipe(
            title="One Pot Chicken and Rice",
            other_tags="healthy",
            ingredients="Chicken (1lb)\nRice (1 cup)",
            steps="Fry the rice for one minute\nAdd water to the rice\nPut the chicken on top of the rice\nCover pot with a lid and boil under low heat for 20min",
        )

        self.recipe3 = create_test_recipe(
            title="Spaghetti Carbonara",
            ingredients="Spaghetti (200g)\nEggs (2)\nCheese (200g)",
            steps="Cook the spaghetti in salted water for 9 min\nDrain the water and mix the eggs and cheese in while still hot",
        )

    def test_all_recipes_url(self):
        """test correct url pattern"""
        self.assertEqual(self.url, "/all_recipes/")

    def test_get_all_recipes(self):
        """test view returns correct status and template"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recipes/all_recipes.html")

    def test_all_recipes_list_is_in_context(self):
        """test all recipes are in context"""
        response = self.client.get(self.url)
        recipes = response.context["recipes"]
        self.assertIn(self.recipe1, recipes)
        self.assertIn(self.recipe2, recipes)
        self.assertIn(self.recipe3, recipes)

    def test_login_required(self):
        """test login is required to access view"""
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_all_recipes_with_exactly_25_recipes(self):
        """test pagination with exactly 25 recipes shows one page"""
        Recipe.objects.all().delete()
        create_test_recipes(count=25)
        response = self.client.get(self.url)
        self.assertEqual(response.context["page_object"].paginator.num_pages, 1)
        self.assertFalse(response.context["page_object"].has_other_pages())

    def test_all_recipes_with_26_recipes(self):
        """test pagination with 26 recipes shows two pages"""
        Recipe.objects.all().delete()
        create_test_recipes(count=26)
        response = self.client.get(self.url)
        self.assertEqual(response.context["page_object"].paginator.num_pages, 2)

    def test_all_recipes_ordering(self):
        """test that recipes are ordered by publication date newest first"""
        Recipe.objects.all().delete()
        old_recipe = create_test_recipe(
            publication_date=timezone.now().date() - timedelta(days=10),
        )
        new_recipe = create_test_recipe()
        response = self.client.get(self.url)
        recipes = response.context["recipes"]
        self.assertEqual(recipes[0], new_recipe)
        self.assertEqual(recipes[1], old_recipe)

    def test_pagination_works(self):
        """test pagination correctly splits recipes across pages"""
        Recipe.objects.all().delete()
        create_test_recipes(count=55)

        response = self.client.get(self.url)
        self.assertEqual(response.context["page_object"].paginator.num_pages, 3)
        self.assertEqual(response.context["page_object"].paginator.count, 55)

    def test_invalid_page_number(self):
        """test handling of invalid page parameter"""
        response = self.client.get(self.url + "?page=999")
        self.assertEqual(response.status_code, 200)

    def test_non_numeric_page_parameter(self):
        """test handling of non-numeric page parameter"""
        response = self.client.get(self.url + "?page=abc")
        self.assertEqual(response.status_code, 200)
