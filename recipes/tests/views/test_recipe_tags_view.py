from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model

User = get_user_model()


class RecipeTagsViewTests(TestCase):
    """
    Tests for POST behaviour of recipe_tags_view.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="pass"
        )
        self.client.login(username="testuser", password="pass")
        self.url = reverse("create_recipe_tags")

        session = self.client.session
        session["recipe_form_data"] = {"form_data": {"title": "Test"}}
        session.save()

    @patch("recipes.views.recipe_tags_view.RecipeFormHandler.handle_tags_post")
    def test_post_redirects_when_handler_returns_response(self, mock_post):
        """ Redirects when handler returns HttpResponseRedirect. """
        mock_post.return_value = HttpResponseRedirect("/dummy")
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 302)

    @patch("recipes.views.recipe_tags_view.RecipeFormHandler.handle_tags_post")
    @patch("recipes.views.recipe_tags_view.RecipeFormHandler.get_tags_context")
    def test_post_renders_page_when_handler_returns_none(self, mock_context, mock_post):
        """ Renders template when handler returns None. """
        mock_post.return_value = None

        mock_context.return_value = {
            "course_tags": [],
            "dietary_tags": [],
            "cuisine_tags": [],
            "other_tags": [],
            "mode": "create",
            "is_owner": False,
            "has_image": False,
            "recipe": None,      
        }

        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "recipes/recipe_tags_form.html")