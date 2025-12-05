from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from unittest.mock import patch

from recipes.models import Recipe, User
from recipes.handlers.recipe_detail_handler import RecipeDetailHandler


class RecipeDetailCostContextTests(TestCase):
    """
    Tests for cost context in RecipeDetailHandler.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='@testuser',
            email='test@example.com',
            password='Password123'
        )
        self.recipe = Recipe.objects.create(
            author=self.user,
            title="Cost Test Recipe",
            publication_date=timezone.now().date(),
            ingredients="Test (1)",
            steps="Test",
            servings=2
        )
        self.factory = RequestFactory()
        
    def get_authenticated_request(self):
        request = self.factory.get("/")
        request.user = self.user
        return request

    @patch("recipes.handlers.recipe_detail_handler.get_cost_estimate_data")
    def test_cost_context_when_show_cost_true(self, mock_cost):
        mock_cost.return_value = {
            "total_cost": 5.50,
            "cost_per_serving": 2.75
        }

        request = self.factory.get("/recipe/1?show_cost=true")
        request.user = self.user
        handler = RecipeDetailHandler(request, self.recipe.id)

        # Minimal scaled ingredients context.
        scaled_ingredients = ["Test (1)"]

        result = handler.get_cost_context(scaled_ingredients)
        self.assertEqual(result["cost_estimate"]["total_cost"], 5.50)
        self.assertIsNone(result["cost_error"])
        mock_cost.assert_called_once()
    
    def test_determine_ownership_unauthenticated(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()
        handler = RecipeDetailHandler(request, self.recipe.id)
        self.assertFalse(handler.determine_ownership())

    def test_get_user_context(self):
        request = self.get_authenticated_request()
        handler = RecipeDetailHandler(request, self.recipe.id)
        context = handler.get_user_context()
        self.assertIn('user_rating', context)
        self.assertIn('user_has_flagged', context)
    
    @patch("recipes.handlers.recipe_detail_handler.get_cost_estimate_data")
    def test_cost_context_error(self, mock_cost):
        mock_cost.side_effect = Exception("Boom")

        request = self.factory.get("/recipe/1?show_cost=true")
        request.user = self.user

        handler = RecipeDetailHandler(request, self.recipe.id)
        result = handler.get_cost_context(["Test (1)"])

        self.assertIsNone(result["cost_estimate"])
        self.assertEqual(result["cost_error"], "Boom")

    def test_cost_context_not_triggered_without_show_cost(self):
        request = self.factory.get("/recipe/1")  # NO ?show_cost=true
        request.user = self.user

        handler = RecipeDetailHandler(request, self.recipe.id)
        result = handler.get_cost_context(["Test (1)"])

        self.assertIsNone(result["cost_estimate"])
        self.assertIsNone(result["cost_error"])
    
    def test_get_context_full(self):
        request = self.get_authenticated_request()
        handler = RecipeDetailHandler(request, self.recipe.id)
        
        context = handler.get_context()

        self.assertIn('recipe', context)
        self.assertIn('steps', context)
        self.assertIn('is_owner', context)

        # Scaling
        self.assertIn('scaled_ingredients', context)
        self.assertIn('desired_servings', context)

        # Rating and flags
        self.assertIn('user_rating', context)
        self.assertIn('user_has_flagged', context)

        # Cost context defaults
        self.assertIn('cost_estimate', context)
        self.assertIn('cost_error', context)
    
    def test_parse_servings_param_zero_or_negative(self):
        request = self.factory.get("/recipe/1?servings=0")
        request.user = self.user

        handler = RecipeDetailHandler(request, self.recipe.id)

        self.assertEqual(handler.desired_servings, self.recipe.servings)

        # Try negative
        request = self.factory.get("/recipe/1?servings=-5")
        request.user = self.user
        handler = RecipeDetailHandler(request, self.recipe.id)
        self.assertEqual(handler.desired_servings, self.recipe.servings)
    
    def test_parse_servings_param_invalid_string(self):
        request = self.factory.get("/recipe/1?servings=abc")
        request.user = self.user

        handler = RecipeDetailHandler(request, self.recipe.id)

        # Should fall back to recipe.servings
        self.assertEqual(handler.desired_servings, self.recipe.servings)
    
    def test_parse_servings_param_none(self):
        request = self.factory.get("/recipe/1?servings=")
        request.user = self.user

        handler = RecipeDetailHandler(request, self.recipe.id)

        self.assertEqual(handler.desired_servings, self.recipe.servings)


