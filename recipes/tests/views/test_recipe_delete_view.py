from django.test import TestCase
from django.urls import reverse
from recipes.models import Recipe, User
from datetime import date
from recipes.tests.utils import create_test_user, create_test_recipe, get_default_user

class RecipeDeleteViewTestCase(TestCase):
    def setUp(self):
        self.user = get_default_user()
        self.recipe = create_test_recipe(
            title='Test Recipe',
            ingredients='Tomato\nGarlic',
            steps='Chop tomatoes\nCook garlic'
        )
        self.client.login(username='@johndoe', password='Password123')
        self.url = reverse('delete_recipe', kwargs={'recipe_id': self.recipe.id})
    
    def test_get_shows_confirmation(self):
        """Test that GET request shows confirmation page"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Recipe')
    
    def test_post_deletes_recipe(self):
        """Test that POST request deletes the recipe"""
        response = self.client.post(self.url)
        self.assertFalse(Recipe.objects.filter(id=self.recipe.id).exists())
        self.assertRedirects(response, reverse('all_recipes'))
    
    def test_cannot_delete_other_users_recipe(self):
        """Test that users cannot delete recipes they don't own"""
        other_user = create_test_user(username='@otheruser')
        self.client.login(username='@otheruser', password='Password123')
        
        response = self.client.post(self.url)
        # Check if view returns 403 or 404 (both are valid for unauthorized access)
        self.assertIn(response.status_code, [403, 404])