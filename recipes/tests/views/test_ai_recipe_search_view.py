import json
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

    def test_post_without_context_shows_error(self):
        """test post without context shows error"""
        self.client.login(username='@testuser', password='Password123')
        response = self.client.post(self.url, {})
        messages = list(response.context['messages'])
        self.assertTrue(any('Please describe your situation' in str(m) for m in messages))

    def test_post_with_empty_context_shows_error(self):
        """test post with empty context shows error"""
        self.client.login(username='@testuser', password='Password123')
        response = self.client.post(self.url, {'context': ''})
        messages = list(response.context['messages'])
        self.assertTrue(any('Please describe your situation' in str(m) for m in messages))

    @patch('recipes.views.ai_recipe_search_view.openai.ChatCompletion.create')
    def test_successful_search_with_results(self, mock_openai):
        """test successful search returns results"""
        self.client.login(username='@testuser', password='Password123')
        
        search_params = MagicMock()
        search_params.choices = [MagicMock()]
        search_params.choices[0].message.content = json.dumps({
            "search_query": "vegan",
            "dietary_filters": ["vegan"],
            "cuisine_filters": [],
            "other_filters": [],
            "sort_by": "date_newest"
        })
        
        ranking = MagicMock()
        ranking.choices = [MagicMock()]
        ranking.choices[0].message.content = json.dumps({
            "top_picks": [{
                "recipe_id": self.recipe2.id,
                "title": "Vegan Curry",
                "reason": "Perfect vegan option"
            }],
            "search_explanation": "Found vegan recipes"
        })
        
        mock_openai.side_effect = [search_params, ranking]
        response = self.client.post(self.url, {'context': 'I want vegan food'})
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['show_results'])
        self.assertIn('top_picks', response.context)
        self.assertIn('search_explanation', response.context)

    @patch('recipes.views.ai_recipe_search_view.openai.ChatCompletion.create')
    def test_search_with_no_results(self, mock_openai):
        """test search with no matching recipes"""
        self.client.login(username='@testuser', password='Password123')
        
        search_params = MagicMock()
        search_params.choices = [MagicMock()]
        search_params.choices[0].message.content = json.dumps({
            "search_query": "nonexistent",
            "dietary_filters": [],
            "cuisine_filters": [],
            "other_filters": [],
            "sort_by": "date_newest"
        })
        
        mock_openai.return_value = search_params
        response = self.client.post(self.url, {'context': 'I want something impossible'})
        
        self.assertTrue(response.context['no_results'])
        self.assertTrue(response.context['show_results'])

    @patch('recipes.views.ai_recipe_search_view.openai.ChatCompletion.create')
    def test_all_context_variables_present(self, mock_openai):
        """test all required context variables are present"""
        self.client.login(username='@testuser', password='Password123')
        
        search_params = MagicMock()
        search_params.choices = [MagicMock()]
        search_params.choices[0].message.content = json.dumps({
            "search_query": "pasta",
            "dietary_filters": [],
            "cuisine_filters": [],
            "other_filters": [],
            "sort_by": "date_newest"
        })
        
        ranking = MagicMock()
        ranking.choices = [MagicMock()]
        ranking.choices[0].message.content = json.dumps({
            "top_picks": [{"recipe_id": self.recipe1.id, "title": "Pasta", "reason": "Good"}],
            "search_explanation": "Found pasta"
        })
        
        mock_openai.side_effect = [search_params, ranking]
        response = self.client.post(self.url, {'context': 'I want pasta'})
        
        self.assertIn('user_context', response.context)
        self.assertIn('search_params', response.context)
        self.assertIn('search_explanation', response.context)
        self.assertIn('top_picks', response.context)
        self.assertIn('top_pick_ids', response.context)
        self.assertIn('total_count', response.context)
        self.assertIn('view_all_url', response.context)

    @patch('recipes.views.ai_recipe_search_view.openai.ChatCompletion.create')
    def test_user_context_preserved(self, mock_openai):
        """test user input is preserved in context"""
        self.client.login(username='@testuser', password='Password123')
        
        search_params = MagicMock()
        search_params.choices = [MagicMock()]
        search_params.choices[0].message.content = json.dumps({
            "search_query": "quick",
            "dietary_filters": [],
            "cuisine_filters": [],
            "other_filters": ["quick"],
            "sort_by": "date_newest"
        })
        
        ranking = MagicMock()
        ranking.choices = [MagicMock()]
        ranking.choices[0].message.content = json.dumps({
            "top_picks": [{"recipe_id": self.recipe1.id, "title": "Pasta", "reason": "Quick"}],
            "search_explanation": "Found quick recipes"
        })
        
        mock_openai.side_effect = [search_params, ranking]
        user_input = 'I need something quick for dinner'
        response = self.client.post(self.url, {'context': user_input})
        
        self.assertEqual(response.context['user_context'], user_input)

    @patch('recipes.views.ai_recipe_search_view.openai.ChatCompletion.create')
    def test_openai_api_error(self, mock_openai):
        """test openai api error shows error message"""
        self.client.login(username='@testuser', password='Password123')
        mock_openai.side_effect = Exception('API Error')
        
        response = self.client.post(self.url, {'context': 'I want pasta'})
        
        messages = list(response.context['messages'])
        self.assertTrue(any('An error occurred' in str(m) for m in messages))

    @patch('recipes.views.ai_recipe_search_view.openai.ChatCompletion.create')
    def test_invalid_json_response(self, mock_openai):
        """test invalid json from ai shows error"""
        self.client.login(username='@testuser', password='Password123')
        
        invalid = MagicMock()
        invalid.choices = [MagicMock()]
        invalid.choices[0].message.content = 'not valid json'
        mock_openai.return_value = invalid
        
        response = self.client.post(self.url, {'context': 'I want pasta'})
        
        messages = list(response.context['messages'])
        self.assertTrue(any('An error occurred' in str(m) for m in messages))

    @patch('recipes.views.ai_recipe_search_view.openai.ChatCompletion.create')
    def test_exception_preserves_user_context(self, mock_openai):
        """test user context preserved on error"""
        self.client.login(username='@testuser', password='Password123')
        mock_openai.side_effect = Exception('Error')
        
        user_input = 'I want Italian food'
        response = self.client.post(self.url, {'context': user_input})
        
        self.assertEqual(response.context['user_context'], user_input)