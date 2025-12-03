from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from unittest.mock import patch, MagicMock
from recipes.models import User
import json


class AIRecipeGeneratorViewTestCase(TestCase):
    """Tests for AI Recipe Generator functionality."""

    def setUp(self):
        """Set up test user and client."""
        self.user = User.objects.create_user(
            username='@testuser',
            first_name='Test',
            last_name='User',
            email='test@example.com',
            password='Password123'
        )

        self.client = Client()
        self.url = reverse('ai_recipe_generator')

        # Mock AI response
        self.mock_recipe = {
            "title": "Test Pasta Recipe",
            "description": "A delicious test pasta",
            "prep_time": "10 minutes",
            "cook_time": "15 minutes",
            "servings": 2,
            "difficulty": "Easy",
            "ingredients": [
                "200g pasta",
                "2 cloves garlic",
                "100ml olive oil"
            ],
            "steps": [
                "Boil water and cook pasta",
                "Sauté garlic in olive oil",
                "Mix everything together"
            ],
            "tips": ["Use fresh garlic", "Don't overcook pasta"],
            "dietary_info": ["vegetarian"]
        }

    def test_ai_recipe_generator_requires_login(self):
        """Test that AI recipe generator requires authentication."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/log_in/', response.url)

    def test_ai_recipe_generator_get_shows_form(self):
        """Test that GET request shows the form."""
        self.client.login(username='@testuser', password='Password123')

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ai/ai_recipe_generator.html')
        self.assertContains(response, 'What do you want to eat?')
        self.assertContains(response, 'Describe what you want to cook and Chef AI will create a recipe for you!')

    def test_empty_prompt_shows_error(self):
        """Test that empty prompt shows error message."""
        self.client.login(username='@testuser', password='Password123')

        response = self.client.post(self.url, {'prompt': ''})

        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertIn('Please describe what you want to cook', str(messages[0]))

    @patch('openai.ChatCompletion.create')
    def test_successful_recipe_generation(self, mock_openai):
        """Test successful AI recipe generation."""
        self.client.login(username='@testuser', password='Password123')

        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(self.mock_recipe)
        mock_openai.return_value = mock_response

        response = self.client.post(self.url, {
            'prompt': 'I want a quick pasta dish'
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['show_results'])
        self.assertEqual(response.context['recipe']['title'], 'Test Pasta Recipe')
        self.assertContains(response, 'Test Pasta Recipe')
        self.assertContains(response, 'A delicious test pasta')

    @patch('openai.ChatCompletion.create')
    def test_ai_receives_correct_prompt(self, mock_openai):
        """Test that AI receives the user's prompt correctly."""
        self.client.login(username='@testuser', password='Password123')

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(self.mock_recipe)
        mock_openai.return_value = mock_response

        user_prompt = 'I want a vegetarian meal'
        self.client.post(self.url, {'prompt': user_prompt})

        # Verify OpenAI was called
        self.assertTrue(mock_openai.called)

        # Check that user prompt was included in the AI request
        call_args = mock_openai.call_args
        messages = call_args[1]['messages']
        user_message = messages[1]['content']
        self.assertIn(user_prompt, user_message)

    @patch('openai.ChatCompletion.create')
    def test_invalid_json_response_shows_error(self, mock_openai):
        """Test that invalid JSON from AI shows error message."""
        self.client.login(username='@testuser', password='Password123')

        # Mock invalid JSON response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "This is not JSON"
        mock_openai.return_value = mock_response

        response = self.client.post(self.url, {
            'prompt': 'I want pasta'
        })

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertIn('invalid format', str(messages[0]).lower())

    @patch('openai.ChatCompletion.create')
    def test_api_timeout_shows_error(self, mock_openai):
        """Test that API timeout shows appropriate error."""
        self.client.login(username='@testuser', password='Password123')

        # Mock timeout error
        import openai
        mock_openai.side_effect = openai.error.Timeout("Request timed out")

        response = self.client.post(self.url, {
            'prompt': 'I want pasta'
        })

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertIn('timed out', str(messages[0]).lower())

    @patch('openai.ChatCompletion.create')
    def test_api_error_shows_error(self, mock_openai):
        """Test that API errors show appropriate message."""
        self.client.login(username='@testuser', password='Password123')

        # Mock API error
        import openai
        mock_openai.side_effect = openai.error.APIError("API Error")

        response = self.client.post(self.url, {
            'prompt': 'I want pasta'
        })

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertIn('api error', str(messages[0]).lower())

    @patch('openai.ChatCompletion.create')
    def test_recipe_displays_all_fields(self, mock_openai):
        """Test that all recipe fields are displayed correctly."""
        self.client.login(username='@testuser', password='Password123')

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(self.mock_recipe)
        mock_openai.return_value = mock_response

        response = self.client.post(self.url, {
            'prompt': 'I want pasta'
        })

        # Check all fields are in response
        self.assertContains(response, 'Test Pasta Recipe')
        self.assertContains(response, 'A delicious test pasta')
        self.assertContains(response, '10 minutes')
        self.assertContains(response, '15 minutes')
        self.assertContains(response, '2')
        self.assertContains(response, 'Easy')
        self.assertContains(response, '200g pasta')
        self.assertContains(response, 'Boil water and cook pasta')
        self.assertContains(response, 'Use fresh garlic')
        self.assertContains(response, 'vegetarian')

    @patch('openai.ChatCompletion.create')
    def test_user_prompt_preserved_on_error(self, mock_openai):
        """Test that user's prompt is preserved when there's an error."""
        self.client.login(username='@testuser', password='Password123')

        # Mock error
        mock_openai.side_effect = Exception("Test error")

        user_prompt = 'I want a test meal'
        response = self.client.post(self.url, {
            'prompt': user_prompt
        })

        # User prompt should still be in context
        self.assertEqual(response.context['user_prompt'], user_prompt)

    @patch('openai.ChatCompletion.create')
    def test_recipe_with_no_tips(self, mock_openai):
        """Test recipe generation with no tips."""
        self.client.login(username='@testuser', password='Password123')

        recipe_no_tips = self.mock_recipe.copy()
        recipe_no_tips['tips'] = []

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(recipe_no_tips)
        mock_openai.return_value = mock_response

        response = self.client.post(self.url, {
            'prompt': 'I want pasta'
        })

        # Should still render successfully
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['show_results'])

    @patch('openai.ChatCompletion.create')
    def test_recipe_with_no_dietary_info(self, mock_openai):
        """Test recipe generation with no dietary info."""
        self.client.login(username='@testuser', password='Password123')

        recipe_no_dietary = self.mock_recipe.copy()
        recipe_no_dietary['dietary_info'] = []

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(recipe_no_dietary)
        mock_openai.return_value = mock_response

        response = self.client.post(self.url, {
            'prompt': 'I want pasta'
        })

        # Should still render successfully
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['show_results'])


class AIRecipeGeneratorIntegrationTestCase(TestCase):
    """Integration tests for AI Recipe Generator (requires API key)."""

    def setUp(self):
        """Set up test user."""
        self.user = User.objects.create_user(
            username='@testuser',
            first_name='Test',
            last_name='User',
            email='test@example.com',
            password='Password123'
        )
        self.client = Client()
        self.url = reverse('ai_recipe_generator')

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    def test_api_key_loaded_from_environment(self):
        """Test that API key is loaded from environment."""
        import os
        key = os.environ.get('OPENAI_API_KEY')
        self.assertEqual(key, 'test-key')