from django.test import TestCase
from django.urls import reverse
from recipes.models import Recipe, User
from datetime import date

class RecipeDeleteViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='Password123',
            first_name='Test',
            last_name='User'
        )
        self.recipe = Recipe.objects.create(
            title='Test Recipe',
            author=self.user,
            publication_date=date.today(),
            ingredients='Tomato\nGarlic',
            steps='Chop tomatoes\nCook garlic'
        )
        self.client.login(username='testuser', password='Password123')
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
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='Password123'
        )
        self.client.login(username='otheruser', password='Password123')
        
        response = self.client.post(self.url)
        # Check if view returns 403 or 404 (both are valid for unauthorized access)
        self.assertIn(response.status_code, [403, 404])

    def test_delete_nonexistent_recipe_returns_error(self):
        """Test that deleting a nonexistent recipe returns 404"""
        url = reverse('delete_recipe', kwargs={'recipe_id': 99999})
        self.client.login(username='testuser', password='Password123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)