from django.test import TestCase
from django.urls import reverse
from recipes.models import Recipe, User
from django.utils import timezone 
from unittest.mock import patch
from recipes.tests.utils import create_test_recipe, get_default_user

class RecipeDetailViewTestCase(TestCase):
    """ Tests for the recipe detail view. """

    fixtures = [
        'recipes/tests/fixtures/default_user.json'
    ]

    def setUp(self):
        self.user = get_default_user()
        self.client.login(username='@johndoe', password='Password123')

        self.recipe = create_test_recipe(
            title="Korean Noodles",                        
            ingredients="test (1)",
            steps="test"
        )
        self.url = reverse('recipe_detail', kwargs={'recipe_id': self.recipe.id})

    def test_recipe_detail_url(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_recipe_detail_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'recipes/recipe.html')

    # Test recipe object is passed in context
    def test_recipe_detail_context(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context['recipe'], self.recipe)

    # Test accessing non-existent recipe returns 404
    def test_invalid_recipe_id_returns_404(self):
        url = reverse('recipe_detail', kwargs={'recipe_id': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    # Test negative recipe ID returns 404
    def test_recipe_detail_with_negative_id(self):
        response = self.client.get("/recipe/-1")
        self.assertEqual(response.status_code, 404)

    # Test zero recipe ID returns 404
    def test_recipe_detail_with_zero_id(self):
        response = self.client.get("/recipe/0")
        self.assertEqual(response.status_code, 404)

    # Test very large recipe ID returns 404
    def test_recipe_detail_with_very_large_id(self):
        response = self.client.get("/recipe/999999999")
        self.assertEqual(response.status_code, 404)

    def test_recipe_detail_displays_title(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Korean Noodles")

    def test_recipe_detail_displays_ingredients(self):
        """ Test that recipe ingredients are displayed on the page. """
        response = self.client.get(self.url)
        self.assertContains(response, "test (1)")
        self.assertContains(response, self.recipe.ingredients)

    def test_recipe_detail_displays_steps(self):
        """ Test that recipe steps are displayed on the page. """
        response = self.client.get(self.url)
        self.assertContains(response, "test")
        self.assertContains(response, self.recipe.steps)
    
    def test_recipe_detail_displays_author(self):
        response = self.client.get(self.url)
        self.assertContains(response, self.user.username)
    
    def test_recipe_detail_displays_publication_date(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        # Check that the formatted date appears
        formatted_date = self.recipe.publication_date.strftime('%b. %-d, %Y')
        self.assertContains(response, formatted_date)
    
    def test_recipe_with_multiple_ingredients(self):
        """ Test recipe with multiple ingredients displays all correctly. """
        recipe = create_test_recipe(
            ingredients="Flour (500g)\nSugar (200g)\nEggs (3)\nMilk (250ml)\nButter (100g)"
        )

        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        # Check all ingredients are present
        self.assertContains(response, "Flour")
        self.assertContains(response, "500g")
        self.assertContains(response, "Sugar")
        self.assertContains(response, "200g")
        self.assertContains(response, "Eggs")
        self.assertContains(response, "Milk")
        self.assertContains(response, "Butter")

    def test_recipe_with_multiple_steps(self):
        """ Test recipe with multiple steps displays all in order. """
        recipe = create_test_recipe(steps="Boil water\nAdd salt\nReduce heat\nSimmer for 10 minutes\nServe hot")

        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        # Check all steps are present
        self.assertContains(response, "Boil water")
        self.assertContains(response, "Add salt")
        self.assertContains(response, "Reduce heat")
        self.assertContains(response, "Simmer for 10 minutes")
        self.assertContains(response, "Serve hot")

    # Test that update button is present
    def test_recipe_detail_has_update_button(self):
        """ Test that update button is present. """
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Update this recipe')
        update_url = reverse('update_recipe', kwargs={'recipe_id': self.recipe.id})
        self.assertContains(response, update_url)

    def test_recipe_detail_has_delete_button(self):
        """ Test that delete button is present. """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Delete this recipe')
        delete_url = reverse('delete_recipe', kwargs={'recipe_id': self.recipe.id})
        self.assertContains(response, delete_url)

    def test_recipe_detail_has_back_button(self):
        """ Test that back to home button is present. """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Go back home')
        home_url = reverse('home')
        self.assertContains(response, home_url)