from django.test import TestCase, RequestFactory
from unittest.mock import patch, MagicMock
from recipes.models import User, Recipe, Rating, Flag
from recipes.helpers.recipe_detail_helpers import (
    scale_ingredient,
    get_scaled_ingredients_context,
    get_user_rating,
    has_user_flagged_recipe,
    get_recipe_tag_display_context,
    get_recipe_time_display_context,
    create_cost_prompt,
    call_openai_for_cost,
    parse_cost_response,
    get_cost_estimate_data,
)
from datetime import date
import json


class ScaleIngredientTests(TestCase):
    """
    Test ingredient scaling.
    """

    def test_scale_whole_number(self):
        """Scale ingredient with whole number."""
        result = scale_ingredient("400g pasta", 2.0)
        self.assertEqual(result, "800g pasta")

    def test_scale_decimal(self):
        """Scale ingredient with decimal."""
        result = scale_ingredient("200g pasta", 1.5)
        self.assertEqual(result, "300g pasta")

    def test_scale_fraction(self):
        """Scale ingredient with fraction."""
        result = scale_ingredient("1/2 cup sugar", 2.0)
        self.assertEqual(result, "1 cup sugar")


class GetScaledIngredientsContextTests(TestCase):
    """
    Test scaled ingredients context.
    """

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="@testuser", email="test@example.com", password="Password123"
        )

        self.recipe = Recipe.objects.create(
            author=self.user,
            title="Test Recipe",
            publication_date=date.today(),
            ingredients="Pasta (400g)\nEggs (2)",
            steps="Cook",
            servings=2,
        )

    def test_get_scaled_context_double_servings(self):
        """Test doubling servings."""
        result = get_scaled_ingredients_context(self.recipe, 4)

        self.assertEqual(result["desired_servings"], 4)
        self.assertEqual(result["scaling_factor"], 2.0)
        self.assertEqual(len(result["scaled_ingredients"]), 2)

    def test_get_scaled_context_invalid_servings(self):
        """Test invalid servings defaults to recipe servings."""
        result = get_scaled_ingredients_context(self.recipe, 0)

        self.assertEqual(result["desired_servings"], self.recipe.servings)


class GetUserRatingTests(TestCase):
    """
    Test get_user_rating helper.
    """

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="@testuser", email="test@example.com", password="Password123"
        )

        self.recipe = Recipe.objects.create(
            author=self.user,
            title="Test Recipe",
            publication_date=date.today(),
            ingredients="Test (1)",
            steps="Test",
        )

    def test_unauthenticated_user_returns_none(self):
        """Unauthenticated user returns None."""
        from django.contrib.auth.models import AnonymousUser

        user = AnonymousUser()

        result = get_user_rating(self.recipe, user)
        self.assertIsNone(result)

    def test_user_with_rating_returns_rating(self):
        """User with rating returns rating."""
        rating = Rating.objects.create(recipe=self.recipe, user=self.user, stars=5)

        result = get_user_rating(self.recipe, self.user)
        self.assertEqual(result, rating)

    def test_user_without_rating_returns_none(self):
        """User without rating returns None."""
        result = get_user_rating(self.recipe, self.user)
        self.assertIsNone(result)


class HasUserFlaggedRecipeTests(TestCase):
    """
    Test has_user_flagged_recipe helper.
    """

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="@testuser", email="test@example.com", password="Password123"
        )

        self.recipe = Recipe.objects.create(
            author=self.user,
            title="Test Recipe",
            publication_date=date.today(),
            ingredients="Test (1)",
            steps="Test",
        )

    def test_unauthenticated_returns_false(self):
        """Unauthenticated user returns False."""
        from django.contrib.auth.models import AnonymousUser

        user = AnonymousUser()

        result = has_user_flagged_recipe(self.recipe, user)
        self.assertFalse(result)

    def test_user_with_flag_returns_true(self):
        """User with flag returns True."""
        Flag.objects.create(recipe=self.recipe, user=self.user)

        result = has_user_flagged_recipe(self.recipe, self.user)
        self.assertTrue(result)

    def test_user_without_flag_returns_false(self):
        """User without flag returns False."""
        result = has_user_flagged_recipe(self.recipe, self.user)
        self.assertFalse(result)


class GetRecipeTagDisplayContextTests(TestCase):
    """
    Test get_recipe_tag_display_context.
    """

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="@testuser", email="test@example.com", password="Password123"
        )

        self.recipe = Recipe.objects.create(
            author=self.user,
            title="Test Recipe",
            publication_date=date.today(),
            ingredients="Test (1)",
            steps="Test",
            course_tags="main,dessert",
            dietary_tags="vegetarian",
            cuisine_tags="Italian",
            other_tags="quick",
        )

    def test_returns_all_tag_lists(self):
        """Returns all tag lists."""
        result = get_recipe_tag_display_context(self.recipe)

        self.assertIn("main", result["course_tags"])
        self.assertIn("dessert", result["course_tags"])
        self.assertIn("vegetarian", result["dietary_tags"])
        self.assertIn("Italian", result["cuisine_tags"])
        self.assertIn("quick", result["other_tags"])


class GetRecipeTimeDisplayContextTests(TestCase):
    """
    Test get_recipe_time_display_context.
    """

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="@testuser", email="test@example.com", password="Password123"
        )

        self.recipe = Recipe.objects.create(
            author=self.user,
            title="Test Recipe",
            publication_date=date.today(),
            ingredients="Test (1)",
            steps="Test",
            prep_time_hours=1,
            prep_time_minutes=30,
            cook_time_hours=2,
            cook_time_minutes=0,
        )

    def test_returns_time_displays(self):
        """Returns formatted time displays."""
        result = get_recipe_time_display_context(self.recipe)

        self.assertIn("prep_time_display", result)
        self.assertIn("cook_time_display", result)
        self.assertIn("total_time_display", result)
        self.assertEqual(result["total_prep_minutes"], 90)
        self.assertEqual(result["total_cook_minutes"], 120)


class CostEstimationTests(TestCase):
    """
    Test cost estimation helpers.
    """

    def test_create_cost_prompt(self):
        """Test creating cost prompt."""
        ingredients = ["Pasta (400g)", "Eggs (2)"]
        prompt = create_cost_prompt(ingredients, 4)

        self.assertIn("Pasta (400g)", prompt)
        self.assertIn("Eggs (2)", prompt)
        self.assertIn("4 servings", prompt)
        self.assertIn("GBP", prompt)

    @patch("openai.ChatCompletion.create")
    def test_call_openai_for_cost(self, mock_openai):
        """Test calling OpenAI for cost."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"total_cost": 5.50}'
        mock_openai.return_value = mock_response

        result = call_openai_for_cost("test prompt")

        self.assertEqual(result, '{"total_cost": 5.50}')
        self.assertTrue(mock_openai.called)

    def test_parse_cost_response(self):
        """Test parsing cost response."""
        ai_response = '{"total_cost": 5.50, "cost_per_serving": 1.38}'
        result = parse_cost_response(ai_response, 4)

        self.assertEqual(result["total_cost"], 5.50)
        self.assertEqual(result["cost_per_serving"], 1.38)
        self.assertEqual(result["servings"], 4)

    @patch("recipes.helpers.recipe_detail_helpers.call_openai_for_cost")
    def test_get_cost_estimate_data_success(self, mock_call):
        """Test successful cost estimation."""
        mock_call.return_value = '{"total_cost": 5.50, "cost_per_serving": 1.38}'

        result = get_cost_estimate_data(["Pasta (400g)"], 4)

        self.assertEqual(result["total_cost"], 5.50)
        self.assertEqual(result["cost_per_serving"], 1.38)

    @patch("recipes.helpers.recipe_detail_helpers.call_openai_for_cost")
    def test_get_cost_estimate_data_error(self, mock_call):
        """Test cost estimation error handling."""
        mock_call.side_effect = Exception("API Error")

        with self.assertRaises(Exception):
            get_cost_estimate_data(["Pasta (400g)"], 4)
