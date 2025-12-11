from django.test import TestCase, RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from unittest.mock import Mock
from recipes.helpers.recipe_redirects import (
    redirect_to_form,
    redirect_to_tags,
    show_success_message,
)


class RecipeRedirectsTestCase(TestCase):
    """Tests for recipe redirect helper functions"""

    def setUp(self):
        self.factory = RequestFactory()

    def _create_mock_handler(self, is_create_mode, recipe_id=None, is_owner=True):
        """Helper to create a mock handler"""
        handler = Mock()
        handler.is_create_mode = is_create_mode
        handler.recipe_id = recipe_id
        handler.is_owner = is_owner
        return handler

    def test_redirect_to_form_create_mode(self):
        """Test redirect_to_form in create mode"""
        handler = self._create_mock_handler(is_create_mode=True)

        response = redirect_to_form(handler)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/create_recipe/")

    def test_redirect_to_form_update_mode(self):
        """Test redirect_to_form in update mode"""
        handler = self._create_mock_handler(is_create_mode=False, recipe_id=123)

        response = redirect_to_form(handler)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/update_recipe/123")

    def test_redirect_to_tags_create_mode(self):
        """Test redirect_to_tags in create mode"""
        handler = self._create_mock_handler(is_create_mode=True)

        response = redirect_to_tags(handler)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/create_recipe/tags/")

    def test_redirect_to_tags_update_mode(self):
        """Test redirect_to_tags in update mode"""
        handler = self._create_mock_handler(is_create_mode=False, recipe_id=456)

        response = redirect_to_tags(handler)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/update_recipe/456/tags/")

    def test_show_success_message_create_mode(self):
        """Test success message in create mode"""
        request = self.factory.get("/")
        request.session = {}
        request._messages = FallbackStorage(request)

        handler = self._create_mock_handler(is_create_mode=True)
        recipe = Mock()
        recipe.title = "Test Recipe"

        show_success_message(request, handler, recipe)

        messages = list(request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Recipe created successfully!")

    def test_show_success_message_update_mode_as_owner(self):
        """Test success message in update mode as owner"""
        request = self.factory.get("/")
        request.session = {}
        request._messages = FallbackStorage(request)

        handler = self._create_mock_handler(
            is_create_mode=False, recipe_id=123, is_owner=True
        )
        recipe = Mock()
        recipe.title = "Updated Recipe"

        show_success_message(request, handler, recipe)

        messages = list(request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), "Successfully updated recipe: Updated Recipe"
        )

    def test_show_success_message_update_mode_not_owner(self):
        """Test success message in update mode as non-owner"""
        request = self.factory.get("/")
        request.session = {}
        request._messages = FallbackStorage(request)

        handler = self._create_mock_handler(
            is_create_mode=False, recipe_id=123, is_owner=False
        )
        recipe = Mock()
        recipe.title = "Modified Recipe"

        show_success_message(request, handler, recipe)

        messages = list(request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), "Created your modified version: Modified Recipe"
        )
