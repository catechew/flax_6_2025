from django.test import TestCase, RequestFactory
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
