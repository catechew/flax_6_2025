from django.urls import reverse
from recipes.tests.views.test_helpers_base import BaseRecipeViewTestCase

"""
Tests for the recipe detail view - tags and cost estimation.
"""

class RecipeDetailViewTestCase(BaseRecipeViewTestCase):

    def setUp(self):
        super().setUp()
        self.recipe = self.create_test_recipe(title="Korean Noodles")
        self.url = reverse('recipe_detail', kwargs={'recipe_id': self.recipe.id})

    def test_recipe_detail_displays_course_tags(self):
        """ Test that course tags are displayed. """
        recipe = self.create_test_recipe(
            title="Tagged Recipe",
            servings=4,
            ingredients="Eggs (2)",
            steps="Fry eggs",
            course_tags="breakfast,main"
        )
        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "breakfast")
        self.assertContains(response, "main")

    def test_recipe_detail_displays_dietary_tags(self):
        recipe = self.create_test_recipe(
            title="Dietary Recipe",
            servings=4,
            ingredients="Tofu (200g)",
            steps="Cook tofu",
            dietary_tags="vegan,gluten-free"
        )
        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "vegan")
        self.assertContains(response, "gluten-free")

    def test_recipe_detail_displays_cuisine_tags(self):
        recipe = self.create_test_recipe(
            title="Cuisine Recipe",
            servings=4,
            ingredients="Pasta (300g)",
            steps="Cook pasta",
            cuisine_tags="Italian,Mediterranean"
        )
        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Italian")
        self.assertContains(response, "Mediterranean")

    def test_recipe_detail_displays_other_tags(self):
        """ Test that other tags are displayed. """
        recipe = self.create_test_recipe(
            title="Quick Recipe",
            servings=2,
            ingredients="Bread (2 slices)",
            steps="Toast bread",
            other_tags="quick,budget"
        )
        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "quick")
        self.assertContains(response, "budget")

    def test_recipe_detail_with_all_tags(self):
        """ Test recipe with all tag types displays correctly. """
        recipe = self.create_test_recipe(
            title="Fully Tagged Recipe",
            servings=4,
            ingredients="Rice (200g)",
            steps="Cook rice",
            course_tags="main",
            dietary_tags="vegan",
            cuisine_tags="Asian",
            other_tags="quick,budget"
        )
        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "main")
        self.assertContains(response, "vegan")
        self.assertContains(response, "Asian")
        self.assertContains(response, "quick")
        self.assertContains(response, "budget")

    def test_cost_estimation_button_present(self):
        """ Test that cost estimation button appears on page. """
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Get Cost Estimate')
        self.assertContains(response, 'Cost Estimate')

    def test_cost_estimation_not_calculated_by_default(self):
        """ Test that cost is not calculated on initial page load. """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Total Cost:')
        self.assertNotContains(response, 'Cost per Serving:')
        self.assertContains(response, 'Click the button to estimate')

    def test_cost_estimation_persists_with_servings_change(self):
        """ Test that cost parameter stays when recalculating servings. """
        response = self.client.get(self.url, {'show_cost': 'true', 'servings': 6})
        
        self.assertEqual(response.status_code, 200)
        # Form should preserve show_cost parameter
        self.assertContains(response, 'name="show_cost"')
        self.assertContains(response, 'value="true"')