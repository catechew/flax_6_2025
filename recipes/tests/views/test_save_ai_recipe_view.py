from django.test import TestCase, Client
from django.urls import reverse
from recipes.models import User


class SaveAIRecipeViewTests(TestCase):
    """Test save AI recipe view functionality."""

    def setUp(self):
        """Set up test client and user."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='@testuser',
            email='test@example.com',
            password='Password123',
            first_name='Test',
            last_name='User'
        )
        self.url = reverse('save_ai_recipe')

    def test_requires_login(self):
        """View requires authentication."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/log_in/', response.url)

    def test_no_ai_recipe_redirects(self):
        """Redirect to generator when no AI recipe in session."""
        self.client.login(username='@testuser', password='Password123')
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, reverse('ai_recipe_generator'))
        messages = list(response.context['messages'])
        self.assertTrue(
            any('No AI recipe found' in str(m) for m in messages)
        )

    def test_successful_transfer_to_form(self):
        """AI recipe successfully transferred to form."""
        self.client.login(username='@testuser', password='Password123')

        # Add AI recipe to session
        session = self.client.session
        session['last_ai_recipe'] = {
            'title': 'Pasta Carbonara',
            'ingredients': ['400g pasta', '2 eggs'],
            'steps': ['Cook pasta', 'Mix eggs'],
            'prep_time': '10 minutes',
            'cook_time': '20 minutes',
            'servings': 2,
            'dietary_info': ['vegetarian'],
        }
        session.save()

        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, reverse('create_recipe'))

        self.assertTrue(self.client.session.get('from_ai_save_button'))

        self.assertIn('ai_recipe_prefill', self.client.session)

    def test_cleans_up_last_ai_recipe(self):
        """last_ai_recipe removed from session after transfer."""
        self.client.login(username='@testuser', password='Password123')

        session = self.client.session
        session['last_ai_recipe'] = {'title': 'Test'}
        session.save()

        self.client.get(self.url)

        self.assertNotIn('last_ai_recipe', self.client.session)

    def test_shows_success_message(self):
        """Success message shown on transfer."""
        self.client.login(username='@testuser', password='Password123')

        session = self.client.session
        session['last_ai_recipe'] = {'title': 'Test'}
        session.save()

        response = self.client.get(self.url, follow=True)
        messages = list(response.context['messages'])

        self.assertTrue(
            any('Recipe loaded' in str(m) for m in messages)
        )