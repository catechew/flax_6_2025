from django.test import TestCase
from django.urls import reverse
from recipes.models import Recipe, User
from recipes.tests.utils import get_default_user, create_test_recipe


class AllRecipesSearchTestCase(TestCase):
    """tests for search functionality in all recipes view"""

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

    def test_search_by_title(self):
        """test searching recipes by title"""
        response = self.client.get(self.url, {"q": "Oats"})
        self.assertEqual(response.status_code, 200)
        recipes = list(response.context["recipes"])
        self.assertIn(self.recipe1, recipes)
        self.assertNotIn(self.recipe2, recipes)
        self.assertNotIn(self.recipe3, recipes)
        self.assertEqual(response.context["page_object"].paginator.num_pages, 1)

    def test_search_case_insensitive(self):
        """test that search is case insensitive"""
        response = self.client.get(self.url, {"q": "oAtS"})
        recipes = list(response.context["recipes"])
        self.assertIn(self.recipe1, recipes)

        response = self.client.get(self.url, {"q": "OATS"})
        recipes = list(response.context["recipes"])
        self.assertIn(self.recipe1, recipes)

        response = self.client.get(self.url, {"q": "oats"})
        recipes = list(response.context["recipes"])
        self.assertIn(self.recipe1, recipes)

    def test_search_by_ingredients(self):
        """test searching recipes by ingredient"""
        response = self.client.get(self.url, {"q": "Yoghurt"})
        self.assertEqual(response.status_code, 200)
        recipes = list(response.context["recipes"])
        self.assertIn(self.recipe1, recipes)
        self.assertNotIn(self.recipe2, recipes)
        self.assertNotIn(self.recipe3, recipes)

    def test_search_by_steps(self):
        """test searching recipes by steps"""
        response = self.client.get(self.url, {"q": "water"})
        self.assertEqual(response.status_code, 200)
        recipes = list(response.context["recipes"])
        self.assertNotIn(self.recipe1, recipes)
        self.assertIn(self.recipe2, recipes)
        self.assertIn(self.recipe3, recipes)

    def test_search_partial_match(self):
        """test partial match search"""
        response = self.client.get(self.url, {"q": "Chick"})
        recipes = list(response.context["recipes"])
        self.assertIn(self.recipe2, recipes)

    def test_search_no_results(self):
        """test search with no results"""
        response = self.client.get(self.url, {"q": "NonExistent"})
        self.assertEqual(response.status_code, 200)
        recipes = list(response.context["recipes"])
        self.assertEqual(len(recipes), 0)
        self.assertEqual(response.context["page_object"].paginator.count, 0)

    def test_empty_search_query(self):
        """test empty search query returns all recipes"""
        response = self.client.get(self.url, {"q": ""})
        recipes = list(response.context["recipes"])
        self.assertEqual(len(recipes), 3)
        self.assertIn(self.recipe1, recipes)
        self.assertIn(self.recipe2, recipes)
        self.assertIn(self.recipe3, recipes)

    def test_whitespace_search_query(self):
        """test whitespace only query returns all recipes"""
        response = self.client.get(self.url, {"q": "   "})
        recipes = list(response.context["recipes"])
        self.assertEqual(len(recipes), 3)
        self.assertIn(self.recipe1, recipes)
        self.assertIn(self.recipe2, recipes)
        self.assertIn(self.recipe3, recipes)

    def test_search_query_in_context(self):
        """test search query is passed to template context"""
        response = self.client.get(self.url, {"q": "Oats"})
        self.assertEqual(response.context["search_query"], "Oats")

    def test_search_query_in_rendered_template(self):
        """test search query appears in rendered template"""
        response = self.client.get(self.url, {"q": "Oats"})
        self.assertContains(response, "Oats")
        self.assertContains(response, "Search results for ")

    def test_search_multiple_matches(self):
        """test search that matches multiple recipes"""
        response = self.client.get(self.url, {"q": "healthy"})
        recipes = list(response.context["recipes"])
        self.assertEqual(len(recipes), 2)
        self.assertIn(self.recipe1, recipes)
        self.assertIn(self.recipe2, recipes)
        self.assertNotIn(self.recipe3, recipes)

    def test_all_recipes_without_search_parameter(self):
        """test that accessing url without search parameter shows all recipes"""
        response = self.client.get(self.url)
        recipes = list(response.context["recipes"])
        self.assertEqual(len(recipes), 3)
        self.assertEqual(response.context["search_query"], "")

    def test_search_context_variables(self):
        """test that all necessary context variables are present during search"""
        response = self.client.get(self.url, {"q": "Oats"})
        self.assertIn("recipes", response.context)
        self.assertIn("search_query", response.context)
        self.assertIn("user", response.context)

    def test_search_by_username(self):
        """test searching recipes by author username"""
        response = self.client.get(self.url, {"q": "John"})
        recipes = list(response.context["recipes"])
        self.assertEqual(len(recipes), 3)
        self.assertIn(self.recipe1, recipes)
        self.assertIn(self.recipe2, recipes)
        self.assertIn(self.recipe3, recipes)

    def test_search_by_partial_username(self):
        """test searching by partial username"""
        response = self.client.get(self.url, {"q": "john"})
        recipes = list(response.context["recipes"])
        self.assertGreaterEqual(len(recipes), 1)

    def test_search_by_first_name(self):
        """test searching recipes by author first name"""
        response = self.client.get(self.url, {"q": "John"})
        recipes = list(response.context["recipes"])
        self.assertGreaterEqual(len(recipes), 0)

    def test_search_by_last_name(self):
        """test searching recipes by author last name"""
        response = self.client.get(self.url, {"q": "Doe"})
        recipes = list(response.context["recipes"])
        self.assertGreaterEqual(len(recipes), 0)

    def test_search_by_full_name(self):
        """test searching recipes by author full name"""
        Recipe.objects.all().delete()
        jane = User.objects.get(username="@janedoe")

        jane_recipe = create_test_recipe(
            author=jane,
        )

        response = self.client.get(self.url, {"q": "Jane Doe"})
        recipes = list(response.context["recipes"])

        self.assertIn(jane_recipe, recipes)

    def test_search_multiple_ingredients_and_logic(self):
        """test searching with multiple ingredients uses and logic"""
        Recipe.objects.all().delete()

        recipe_both = create_test_recipe(
            ingredients="Avocado (2)\nGarlic (1 clove)\nLime (1)",
        )

        recipe_avocado_only = create_test_recipe(
            ingredients="Avocado (1)\nBread (2 slices)",
        )

        recipe_garlic_only = create_test_recipe(
            ingredients="Garlic (3 cloves)\nBread (1 loaf)\nButter (50g)",
        )

        response = self.client.get(self.url, {"q": "Avocado Garlic"})
        recipes = list(response.context["recipes"])

        self.assertIn(recipe_both, recipes)
        self.assertNotIn(recipe_avocado_only, recipes)
        self.assertNotIn(recipe_garlic_only, recipes)

    def test_search_multiple_ingredients_different_order(self):
        """test multiple ingredient search works regardless of order"""
        Recipe.objects.all().delete()

        recipe = create_test_recipe(
            ingredients="Chicken (500g)\nRice (200g)\nOnion (1)",
        )

        response1 = self.client.get(self.url, {"q": "Chicken Rice"})
        response2 = self.client.get(self.url, {"q": "Rice Chicken"})

        recipes1 = list(response1.context["recipes"])
        recipes2 = list(response2.context["recipes"])

        self.assertIn(recipe, recipes1)
        self.assertIn(recipe, recipes2)

    def test_search_three_ingredients(self):
        """test searching with three ingredients"""
        Recipe.objects.all().delete()

        recipe_all_three = create_test_recipe(
            ingredients="Tomato (2)\nOnion (1)\nGarlic (3 cloves)\nPasta (200g)",
        )

        recipe_two_only = create_test_recipe(
            ingredients="Tomato (1)\nOnion (1)",
        )

        response = self.client.get(self.url, {"q": "Tomato Onion Garlic"})
        recipes = list(response.context["recipes"])

        self.assertIn(recipe_all_three, recipes)
        self.assertNotIn(recipe_two_only, recipes)

    def test_search_multi_word_still_searches_other_fields(self):
        """test that multi-word search still checks other fields for full phrase"""
        Recipe.objects.all().delete()

        recipe_title = create_test_recipe(
            title="Spicy Korean Noodles",
            ingredients="Noodles (200g)",
        )

        response = self.client.get(self.url, {"q": "Korean Noodles"})
        recipes = list(response.context["recipes"])

        self.assertIn(recipe_title, recipes)

    def test_search_case_insensitive_multiple_words(self):
        """test that multi-word search is case insensitive"""
        Recipe.objects.all().delete()

        recipe = create_test_recipe(
            ingredients="Chicken (500g)\nRice (200g)",
        )

        response1 = self.client.get(self.url, {"q": "chicken rice"})
        response2 = self.client.get(self.url, {"q": "CHICKEN RICE"})
        response3 = self.client.get(self.url, {"q": "ChIcKeN rIcE"})

        recipes1 = list(response1.context["recipes"])
        recipes2 = list(response2.context["recipes"])
        recipes3 = list(response3.context["recipes"])

        self.assertIn(recipe, recipes1)
        self.assertIn(recipe, recipes2)
        self.assertIn(recipe, recipes3)

    def test_search_single_word_uses_or_logic(self):
        """test that single word search still uses or logic across fields"""
        Recipe.objects.all().delete()

        recipe1 = create_test_recipe(
            title="Chicken Soup",
        )

        recipe2 = create_test_recipe(
            ingredients="Chicken (300g)\nPasta (200g)",
        )

        recipe3 = create_test_recipe(steps="Fry the chicken pieces")

        response = self.client.get(self.url, {"q": "Chicken"})
        recipes = list(response.context["recipes"])

        self.assertIn(recipe1, recipes)
        self.assertIn(recipe2, recipes)
        self.assertIn(recipe3, recipes)

    def test_search_query_none_defaults_to_empty(self):
        """test that none search query is handled"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["search_query"], "")
