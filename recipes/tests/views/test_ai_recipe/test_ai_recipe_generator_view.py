from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from recipes.models import User
from unittest.mock import patch, MagicMock
from recipes.tests.utils import AIRecipeTestMixin
import openai


class AIRecipeGeneratorViewTestCase(AIRecipeTestMixin, TestCase):
    """Tests for AI Recipe Generator functionality."""

    def setUp(self):
        """Set up test user and client."""
        self.user = User.objects.create_user(
            username="@testuser",
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password="Password123",
        )
        self.client = Client()
        self.url = reverse("ai_recipe_generator")
        self.mock_recipe = self.create_mock_recipe_data()

    def test_ai_recipe_generator_requires_login(self):
        """Test that AI recipe generator requires authentication."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/log_in/", response.url)

    def test_ai_recipe_generator_get_shows_form(self):
        """Test that GET request shows the form."""
        self.client.login(username="@testuser", password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ai/ai_recipe_generator.html")
        self.assertContains(response, "What do you want to eat?")

    def test_empty_prompt_shows_error(self):
        """Test that empty prompt shows error message."""
        self.client.login(username="@testuser", password="Password123")
        response = self.client.post(self.url, {"prompt": ""})
        messages = list(response.context["messages"])
        self.assertIn("Please describe what you want to cook", str(messages[0]))

    @patch("openai.ChatCompletion.create")
    def test_successful_recipe_generation(self, mock_openai):
        """Test successful AI recipe generation."""
        self.client.login(username="@testuser", password="Password123")
        mock_openai.return_value = self.create_mock_openai_response(self.mock_recipe)
        response = self.client.post(self.url, {"prompt": "I want pasta"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["show_results"])
        self.assertEqual(response.context["recipe"]["title"], "Test Recipe")

    @patch("openai.ChatCompletion.create")
    def test_ai_receives_correct_prompt(self, mock_openai):
        """Test that AI receives the user's prompt correctly."""
        self.client.login(username="@testuser", password="Password123")
        mock_openai.return_value = self.create_mock_openai_response(self.mock_recipe)
        user_prompt = "I want a vegetarian meal"
        self.client.post(self.url, {"prompt": user_prompt})
        self.assertTrue(mock_openai.called)
        call_args = mock_openai.call_args
        messages = call_args[1]["messages"]
        self.assertIn(user_prompt, messages[1]["content"])

    @patch("openai.ChatCompletion.create")
    def test_invalid_json_response_shows_error(self, mock_openai):
        """Test that invalid JSON from AI shows error message."""
        self.client.login(username="@testuser", password="Password123")
        mock_response = self.create_mock_openai_response(self.mock_recipe)
        mock_response.choices[0].message.content = "This is not JSON"
        mock_openai.return_value = mock_response
        response = self.client.post(self.url, {"prompt": "I want pasta"})
        messages = list(response.context["messages"])
        self.assertIn("invalid format", str(messages[0]).lower())

    @patch("openai.ChatCompletion.create")
    def test_api_timeout_shows_error(self, mock_openai):
        """Test that API timeout shows appropriate error."""
        self.client.login(username="@testuser", password="Password123")
        mock_openai.side_effect = openai.error.Timeout("Request timed out")
        response = self.client.post(self.url, {"prompt": "I want pasta"})
        messages = list(response.context["messages"])
        self.assertIn("timed out", str(messages[0]).lower())

    @patch("openai.ChatCompletion.create")
    def test_api_error_shows_error(self, mock_openai):
        """Test that API errors show appropriate message."""
        self.client.login(username="@testuser", password="Password123")
        mock_openai.side_effect = openai.error.APIError("API Error")
        response = self.client.post(self.url, {"prompt": "I want pasta"})
        messages = list(response.context["messages"])
        self.assertIn("api error", str(messages[0]).lower())

    @patch("openai.ChatCompletion.create")
    def test_recipe_displays_all_fields(self, mock_openai):
        """Test that all recipe fields are displayed correctly."""
        self.client.login(username="@testuser", password="Password123")
        mock_openai.return_value = self.create_mock_openai_response(self.mock_recipe)
        response = self.client.post(self.url, {"prompt": "I want pasta"})
        self.assertContains(response, "Test Recipe")
        self.assertContains(response, "Test description")
        self.assertContains(response, "10 minutes")
        self.assertContains(response, "200g pasta")

    @patch("openai.ChatCompletion.create")
    def test_user_prompt_preserved_on_error(self, mock_openai):
        """Test that user's prompt is preserved when there's an error."""
        self.client.login(username="@testuser", password="Password123")
        mock_openai.side_effect = Exception("Test error")
        user_prompt = "I want a test meal"
        response = self.client.post(self.url, {"prompt": user_prompt})
        self.assertEqual(response.context["user_prompt"], user_prompt)

    @patch("openai.ChatCompletion.create")
    def test_recipe_with_no_tips(self, mock_openai):
        """Test recipe generation with no tips."""
        self.client.login(username="@testuser", password="Password123")
        recipe_no_tips = self.create_mock_recipe_data()
        recipe_no_tips["tips"] = []
        mock_openai.return_value = self.create_mock_openai_response(recipe_no_tips)
        response = self.client.post(self.url, {"prompt": "I want pasta"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["show_results"])

    @patch("openai.ChatCompletion.create")
    def test_recipe_with_no_dietary_info(self, mock_openai):
        """Test recipe generation with no dietary info."""
        self.client.login(username="@testuser", password="Password123")
        recipe_no_dietary = self.create_mock_recipe_data()
        recipe_no_dietary["dietary_info"] = []
        mock_openai.return_value = self.create_mock_openai_response(recipe_no_dietary)
        response = self.client.post(self.url, {"prompt": "I want pasta"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["show_results"])


class AIRecipeGeneratorIntegrationTestCase(TestCase):
    """Integration tests for AI Recipe Generator."""

    def setUp(self):
        """Set up test user."""
        self.user = User.objects.create_user(
            username="@testuser",
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password="Password123",
        )
        self.client = Client()
        self.url = reverse("ai_recipe_generator")

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_api_key_loaded_from_environment(self):
        """Test that API key is loaded from environment."""
        import os

        key = os.environ.get("OPENAI_API_KEY")
        self.assertEqual(key, "test-key")
