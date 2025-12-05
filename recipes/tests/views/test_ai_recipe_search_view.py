from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock
from recipes.models import User, Recipe
from datetime import date


class AIRecipeSearchViewTests(TestCase):
    """Test AI recipe search view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='@testuser',
            email='test@example.com',
            password='Password123',
            first_name='Test',
            last_name='User'
        )

        # Create test recipes
        self.recipe1 = Recipe.objects.create(
            author=self.user,
            title='Pasta Carbonara',
            publication_date=date.today(),
            ingredients='Pasta (400g)\nEggs (2)',
            steps='Cook pasta\nMix with eggs',
            dietary_tags='vegetarian',
        )

        self.recipe2 = Recipe.objects.create(
            author=self.user,
            title='Vegan Curry',
            publication_date=date.today(),
            ingredients='Chickpeas (400g)',
            steps='Cook curry',
            dietary_tags='vegan',
        )

        self.url = reverse('ai_recipe_search')

    def test_redirect_if_not_logged_in(self):
        """Test redirect to login if not authenticated."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_get_displays_form(self):
        """Test GET displays search form."""
        self.client.login(username='@testuser', password='Password123')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ai/ai_recipe_search.html')
