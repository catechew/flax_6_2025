from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch
from django.http import HttpResponseRedirect

User = get_user_model()


class RecipeTagsViewTests(TestCase):
    """
    Tests recipe_tags_view behaviour.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="pass"
        )
        self.client.login(username="testuser", password="pass")
        self.url = reverse("create_recipe_tags")

    def test_redirect_when_missing_form_data(self):
        """If no form data in session then redirect occurs."""
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)

    def test_get_renders_template_with_form_data(self):
        """GET request renders template when form data exists."""
        session = self.client.session
        session["recipe_form_data"] = {
            "form_data": {"title": "Test Recipe"},
            "course_tags": ["breakfast"],
        }
        session.save()

        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "recipes/recipe_tags_form.html")
        self.assertIn("course_tags", resp.context)

    def test_post_with_valid_tag_action(self):
        """POST with tag action triggers redirect."""
        session = self.client.session
        session["recipe_form_data"] = {
            "form_data": {"title": "Test Recipe"},
            "course_tags": [],
            "dietary_tags": [],
            "cuisine_tags": [],
            "other_tags": [],
        }
        session.save()

        resp = self.client.post(self.url, {"add_course_tag": "breakfast"})
        self.assertEqual(resp.status_code, 302)

    def test_post_without_action_renders_page(self):
        """POST without action falls back to rendering page (covers red lines)."""
        session = self.client.session
        session["recipe_form_data"] = {
            "form_data": {"title": "Test Recipe"},
            "course_tags": [],
            "dietary_tags": [],
            "cuisine_tags": [],
            "other_tags": [],
        }
        session.save()

        # POST with no recognized action - handle_tags_post returns None
        resp = self.client.post(self.url, {"random_field": "value"})

        # Should render template (THIS COVERS THE RED LINES!)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "recipes/recipe_tags_form.html")

    def test_post_remove_tag(self):
        """POST to remove a tag."""
        session = self.client.session
        session["recipe_form_data"] = {
            "form_data": {"title": "Test Recipe"},
            "course_tags": ["breakfast"],
        }
        session.save()

        resp = self.client.post(self.url, {"remove_course_tag": "breakfast"})
        self.assertEqual(resp.status_code, 302)

    def test_post_create_recipe(self):
        """POST to finalize recipe creation."""
        session = self.client.session
        session["recipe_form_data"] = {
            "form_data": {
                "title": "Test Recipe",
                "ingredients": "Test (1)",
                "steps": "Test step",
                "servings": 4,
                "prep_time_hours": 0,
                "prep_time_minutes": 30,
                "cook_time_hours": 1,
                "cook_time_minutes": 0,
            },
            "course_tags": ["breakfast"],
            "dietary_tags": [],
            "cuisine_tags": [],
            "other_tags": [],
        }
        session.save()

        resp = self.client.post(self.url, {"create_recipe": "1"})
        self.assertEqual(resp.status_code, 302)

    def test_context_includes_tag_data(self):
        """Context includes all tag categories and options."""
        session = self.client.session
        session["recipe_form_data"] = {
            "form_data": {"title": "Test"},
            "course_tags": ["breakfast"],
            "dietary_tags": ["vegan"],
        }
        session.save()

        resp = self.client.get(self.url)

        self.assertIn("course_tags", resp.context)
        self.assertIn("dietary_tags", resp.context)
        self.assertIn("cuisine_tags", resp.context)
        self.assertIn("other_tags", resp.context)
        self.assertIn("course_options", resp.context)

    @patch("recipes.handlers.recipe_form_handler.RecipeFormHandler.finalise_recipe")
    def test_post_create_recipe(self, mock_finalise):
        """POST to finalize recipe creation."""
        # Mock successful recipe creation
        mock_finalise.return_value = HttpResponseRedirect("/recipes/1/")

        session = self.client.session
        session["recipe_form_data"] = {
            "form_data": {
                "title": "Test Recipe",
                "ingredients": "Test (1)",
                "steps": "Test step",
            },
            "course_tags": ["breakfast"],
            "dietary_tags": [],
            "cuisine_tags": [],
            "other_tags": [],
        }
        session.save()

        resp = self.client.post(self.url, {"create_recipe": "1"})
        self.assertEqual(resp.status_code, 302)
        mock_finalise.assert_called_once()