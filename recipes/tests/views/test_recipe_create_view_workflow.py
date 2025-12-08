from django.test import TestCase
from django.urls import reverse
from recipes.models import Recipe
from recipes.tests.utils import get_default_user, create_test_form_data


class RecipeCreateWorkflowTestCase(TestCase):
    """tests for recipe creation workflow, session management, and edge cases"""
    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json',
    ]

    def setUp(self):
        self.user = get_default_user()
        self.client.login(username='@johndoe', password='Password123')
        self.url = reverse('create_recipe')
        self.form_data = create_test_form_data()

    def _create_recipe(self, title):
        """Helper to create a single recipe."""
        self.form_data['title'] = title
        response = self.client.post(self.url, self.form_data, follow=True)
        response = self.client.post(
            reverse('create_recipe_tags'), 
            {'create_recipe': 'true'}, 
            follow=True
        )
        self.assertEqual(response.status_code, 200)

    def test_creating_multiple_recipes(self):
        """test creating multiple recipes one after another"""
        initial_recipe_count = Recipe.objects.count()
        
        self._create_recipe('Test Recipe 0')
        self._create_recipe('Test Recipe 1')
        self._create_recipe('Test Recipe 2')
        self._create_recipe('Test Recipe 3')
        self._create_recipe('Test Recipe 4')
        
        self.assertEqual(Recipe.objects.count(), initial_recipe_count + 5)

    def test_session_cleared_after_successful_creation(self):
        """test that session data is cleared after recipe creation"""
        self.client.post(self.url, self.form_data, follow=True)
        self.client.post(reverse('create_recipe_tags'), {'create_recipe': 'true'}, follow=True)

        session = self.client.session
        self.assertNotIn('recipe_form_data', session)

    def test_cancel_recipe_creation_url(self):
        """test that cancel url exists"""
        url = reverse('cancel_recipe')
        self.assertEqual(url, '/create_recipe/cancel/')

    def test_cancel_recipe_creation_redirects(self):
        """test that cancel redirects to all_recipes"""
        response = self.client.get(reverse('cancel_recipe'))
        self.assertRedirects(response, reverse('all_recipes'))

    def test_cancel_clears_session(self):
        """test that cancelling clears session data"""
        self.client.post(self.url, self.form_data, follow=True)

        session = self.client.session
        self.assertIn('recipe_form_data', session)

        self.client.get(reverse('cancel_recipe'))

        session = self.client.session
        self.assertNotIn('recipe_form_data', session)

    def test_cancel_without_session_data(self):
        """test cancelling when no session data exists"""
        response = self.client.get(reverse('cancel_recipe'))

        self.assertRedirects(response, reverse('all_recipes'))

    def test_going_back_to_page1_preserves_data(self):
        """test that navigating back to page 1 preserves form data"""
        self.client.post(self.url, self.form_data, follow=True)

        response = self.client.get(self.url)

        form = response.context['form']
        self.assertEqual(form.data.get('title'), 'Test Recipe')