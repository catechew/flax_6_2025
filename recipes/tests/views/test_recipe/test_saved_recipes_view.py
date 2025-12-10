"""
Tests for the saved recipes functionality.
"""
from django.test import TestCase
from django.urls import reverse
from recipes.models import Recipe, User
from django.utils import timezone
from recipes.tests.utils import create_test_recipe, create_test_user, get_default_user

class SavedRecipesViewTestCase(TestCase):

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = get_default_user()
        self.other_user = User.objects.get(username='@janedoe')
        
        self.client.login(username='@johndoe', password='Password123')

        # Create a recipe by the other user
        self.recipe = create_test_recipe(
            author=self.other_user,
            title="Delicious Pasta",
            ingredients="Pasta (500g)\nSauce (1 jar)",
            steps="Boil pasta\nAdd sauce",
            course_tags="main"
        )

        self.list_url = reverse('saved_recipe_list')
        self.toggle_url = reverse('toggle_save_recipe', kwargs={'recipe_id': self.recipe.id})

    def test_saved_recipes_url(self):
        """ Test that the saved recipes URL is correct. """
        self.assertEqual(self.list_url, '/saved_recipes/')

    def test_get_saved_recipes_redirects_when_not_logged_in(self):
        """ Test that accessing saved recipes redirects to login when not authenticated. """
        self.client.logout()
        response = self.client.get(self.list_url)
        redirect_url = reverse('log_in') + f'?next={self.list_url}'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_saved_recipes_when_logged_in(self):
        """ Test that logged-in users can access the saved recipes page. """
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/saved_recipes.html')

    def test_saved_recipes_list_is_empty_initially(self):
        """ Test that the list is empty when no recipes are saved. """
        response = self.client.get(self.list_url)
        self.assertEqual(len(response.context['recipes']), 0)
        self.assertContains(response, "You haven't saved any recipes yet")

    def test_save_recipe_functionality(self):
        """ Test saving a recipe adds it to the user's saved list. """
        # Check initial state
        self.assertEqual(self.user.saved_recipes.count(), 0)

        # Post to toggle URL
        response = self.client.post(self.toggle_url, follow=True)

        # Verify recipe is saved
        self.assertEqual(self.user.saved_recipes.count(), 1)
        self.assertEqual(self.user.saved_recipes.first(), self.recipe)
        
        # Verify it appears on the list page
        response = self.client.get(self.list_url)
        self.assertContains(response, "Delicious Pasta")
        self.assertIn(self.recipe, response.context['recipes'])

    def test_unsave_recipe_functionality(self):
        """Test clicking save again removes the recipe (unsave)."""
        # Manually save recipe first
        self.recipe.saved_by.add(self.user)
        self.assertEqual(self.user.saved_recipes.count(), 1)

        # Post to toggle URL 
        self.client.post(self.toggle_url, follow=True)

        # Verify recipe removed
        self.assertEqual(self.user.saved_recipes.count(), 0)

    def test_toggle_save_redirects_back_to_referer(self):
        """ Test that toggling save redirects back to the page the user came from. """
        referer = reverse('all_recipes')
        headers = {'HTTP_REFERER': referer}
        response = self.client.post(self.toggle_url, **headers)
        self.assertRedirects(response, referer)

    def test_toggle_save_redirects_default_if_no_referer(self):
        """ Test that toggling save redirects to dashboard (or defined default) if no referer. """
        response = self.client.post(self.toggle_url)
        self.assertRedirects(response, reverse('dashboard'))

    def test_toggle_save_requires_login(self):
        """ Test that unauthenticated users cannot toggle save. """
        self.client.logout()
        response = self.client.post(self.toggle_url)
        redirect_url = reverse('log_in') + f'?next={self.toggle_url}'
        self.assertRedirects(response, redirect_url)

    def test_toggle_save_invalid_recipe_id(self):
        """ Test that trying to save a non-existent recipe returns 404. """
        invalid_url = reverse('toggle_save_recipe', kwargs={'recipe_id': 9999})
        response = self.client.post(invalid_url)
        self.assertEqual(response.status_code, 404)

    def test_saved_recipes_does_not_show_unsaved_ones(self):
        """ Test that the list only shows explicitly saved recipes. """
        # Create a second recipe
        recipe2 = create_test_recipe(author=self.other_user)

        # Save only the first recipe
        self.recipe.saved_by.add(self.user)
        response = self.client.get(self.list_url)
        recipes = list(response.context['recipes'])
        self.assertIn(self.recipe, recipes)
        self.assertNotIn(recipe2, recipes)

    def test_saving_own_recipe(self):
        """ Test that a user can save their own recipe. """
        my_recipe = create_test_recipe()
        url = reverse('toggle_save_recipe', kwargs={'recipe_id': my_recipe.id})
        self.client.post(url)
        self.assertTrue(self.user.saved_recipes.filter(id=my_recipe.id).exists())