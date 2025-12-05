from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model 

User = get_user_model()


class RecipeTagsViewTests(TestCase):
    """
    Tests for the Recipe Tags view POST behaviour.
    """
    
    def setUp(self):
        """
        Create and log in a test user. 
        Initialise session data required by the view.
        """
        self.user = User.objects.create_user(
            username="testuser", 
            password="pass"
        )
        self.client.login(username="testuser", password="pass")
        
        # URL for the recipe tags view
        self.url = reverse("create_recipe_tags")

        # Pre populate the session with form data 
        session = self.client.session
        session["recipe_form_data"] = {"title": "Test"}
        session.save()

    @patch("recipes.views.recipe_tags_view.RecipeFormHandler.handle_tags_post")
    def test_post_redirects_when_handler_returns_response(self, mock_post):
        """ 
        Ensure POST request redirects when the handler returns an HttpResponseDirect.
        """
        mock_post.return_value = HttpResponseRedirect("/dummy")
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
    
    @patch("recipes.views.recipe_tags_view.RecipeFormHandler.handle_tags_post")
    @patch("recipes.views.recipe_tags_view.RecipeFormHandler.get_tags_context")
    def test_post_renders_page_when_handler_returns_none(self, mock_context, mock_post):
        mock_post.return_value = None
        mock_context.return_value = {"course_tags": []}

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recipes/recipe_tags_form.html")
