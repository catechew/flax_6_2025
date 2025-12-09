from django.urls import reverse
from recipes.tests.views.test_helpers_base import BaseRecipeViewTestCase  

"""
Tests for the recipe detail view - scaling and time display.
"""

class RecipeDetailViewScalingTests(BaseRecipeViewTestCase): 

    def setUp(self):
        super().setUp()
        self.recipe = self.create_test_recipe(title="Korean Noodles")
        self.url = reverse('recipe_detail', kwargs={'recipe_id': self.recipe.id})

    def test_servings_scaling_doubles_ingredients(self):
        """ Test that doubling servings doubles ingredient quantities. """
        recipe = self.create_test_recipe(
            title="Scalable Recipe",
            servings=2,
            ingredients="Sugar (100g)\nFlour (200g)",
            steps="Mix ingredients"
        )
        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url, {'servings': 4})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "200")
        self.assertContains(response, "400")

    def test_servings_scaling_halves_ingredients(self):
        """ Test that halving servings halves ingredient quantities. """
        recipe = self.create_test_recipe(  # ← Changed to use helper
            title="Halvable Recipe",
            servings=4,
            ingredients="Butter (200g)\nMilk (400ml)",
            steps="Mix ingredients"
        )
        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url, {'servings': 2})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "100")
        self.assertContains(response, "200")

    def test_servings_with_invalid_value_uses_default(self):
        """ Test that invalid servings value falls back to recipe default. """
        recipe = self.create_test_recipe(  # ← Changed
            title="Default Servings Recipe",
            servings=3,
            ingredients="Rice (300g)",
            steps="Cook rice"
        )
        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url, {'servings': 'invalid'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "300")
        self.assertContains(response, "3")

    def test_servings_with_empty_value_uses_default(self):
        """ Test that empty servings value falls back to recipe default. """
        recipe = self.create_test_recipe(  # ← Changed
            title="Empty Servings Test",
            servings=5,
            ingredients="Pasta (500g)",
            steps="Boil pasta"
        )
        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url, {'servings': ''})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "500")
        self.assertContains(response, "5")

    def test_servings_scaling_factor_displayed(self):
        """ Test that scaling factor is displayed when servings are adjusted. """
        recipe = self.create_test_recipe(  # ← Changed
            title="Scaling Display Test",
            servings=2,
            ingredients="Salt (2g)",
            steps="Add salt"
        )
        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url, {'servings': 6})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "scaled by")
        self.assertContains(response, "3.00")

    def test_recipe_detail_displays_prep_time(self):
        """ Test that prep time is displayed when present. """
        recipe = self.create_test_recipe(  # ← Changed
            title="Timed Recipe",
            servings=4,
            ingredients="Flour (500g)",
            steps="Mix flour",
            prep_time_hours=1,
            prep_time_minutes=30
        )
        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Prep:")
        self.assertContains(response, "1 hr 30 min")

    def test_recipe_detail_displays_cook_time(self):
        """ Test that cook time is displayed when present. """
        recipe = self.create_test_recipe(  # ← Changed
            title="Cooked Recipe",
            servings=4,
            ingredients="Chicken (1kg)",
            steps="Cook chicken",
            cook_time_hours=1,
            cook_time_minutes=15
        )
        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cook:")
        self.assertContains(response, "1 hr 15 min")

    def test_recipe_detail_displays_total_time(self):
        """ Test that total time is calculated and displayed. """
        recipe = self.create_test_recipe(  # ← Changed
            title="Full Time Recipe",
            servings=4,
            ingredients="Pasta (500g)",
            steps="Cook pasta",
            prep_time_hours=0,
            prep_time_minutes=15,
            cook_time_hours=0,
            cook_time_minutes=25
        )
        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Total:")
        self.assertContains(response, "40 min")

    def test_recipe_detail_with_zero_times_no_display(self):
        """ Test that recipes with zero times don't show time sections. """
        recipe = self.create_test_recipe(  # ← Changed
            title="No Time Recipe",
            servings=4,
            ingredients="Water (1L)",
            steps="Pour water",
            prep_time_hours=0,
            prep_time_minutes=0,
            cook_time_hours=0,
            cook_time_minutes=0
        )
        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Prep:")
        self.assertNotContains(response, "Cook:")

    def test_recipe_with_only_prep_time_minutes(self):
        """ Test recipe with only minutes (no hours) displays correctly. """
        recipe = self.create_test_recipe(  # ← Changed
            title="Quick Prep Recipe",
            servings=2,
            ingredients="Salad (1 bowl)",
            steps="Mix salad",
            prep_time_hours=0,
            prep_time_minutes=10
        )
        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "10 min")
        self.assertNotContains(response, "0 hr")

    def test_recipe_with_only_hours_no_minutes(self):
        recipe = self.create_test_recipe(  # ← Changed
            title="Long Cook Recipe",
            servings=6,
            ingredients="Stew (1 pot)",
            steps="Simmer stew",
            cook_time_hours=3,
            cook_time_minutes=0
        )
        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "3 hrs")