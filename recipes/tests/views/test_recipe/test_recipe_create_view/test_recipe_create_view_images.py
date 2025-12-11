from django.test import TestCase
from django.urls import reverse
from recipes.models import Recipe
from recipes.tests.utils import (
    get_default_user,
    create_test_image,
    create_test_form_data,
)
from django.core.files.storage import default_storage


class RecipeCreateImagesTestCase(TestCase):
    """tests for recipe creation image upload functionality"""

    fixtures = [
        "recipes/tests/fixtures/default_user.json",
        "recipes/tests/fixtures/other_users.json",
    ]

    def setUp(self):
        self.user = get_default_user()
        self.client.login(username="@johndoe", password="Password123")
        self.url = reverse("create_recipe")
        self.form_data = create_test_form_data()

    def test_create_recipe_with_image_upload_succeeds(self):
        initial_recipe_count = Recipe.objects.count()

        uploaded_file = create_test_image()

        data = self.form_data.copy()
        data["image"] = uploaded_file

        response = self.client.post(self.url, data, format="multipart", follow=True)
        response = self.client.post(
            reverse("create_recipe_tags"), {"create_recipe": "true"}, follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Recipe.objects.count(), initial_recipe_count + 1)
        created_recipe = Recipe.objects.latest("id")
        self.assertTrue(bool(created_recipe.image))

    def test_has_image_context_variable(self):
        """test that has_image context variable is set correctly"""
        uploaded_file = create_test_image()

        data = self.form_data.copy()
        data["image"] = uploaded_file

        self.client.post(self.url, data, format="multipart", follow=True)
        response = self.client.get(reverse("create_recipe_tags"))

        self.assertTrue(response.context["has_image"])

    def test_has_image_false_without_image(self):
        """test that has_image is false when no image uploaded"""
        self.client.post(self.url, self.form_data, follow=True)
        response = self.client.get(reverse("create_recipe_tags"))

        self.assertFalse(response.context["has_image"])

    def test_temp_image_deleted_after_creation(self):
        """test that temporary image is deleted after recipe creation"""
        uploaded_file = create_test_image()
        data = self.form_data.copy()
        data["image"] = uploaded_file
        self.client.post(self.url, data, format="multipart", follow=True)
        session = self.client.session
        temp_path = session.get("recipe_form_data", {}).get("temp_image_path")
        self.client.post(
            reverse("create_recipe_tags"), {"create_recipe": "true"}, follow=True
        )

        self.assertIsNotNone(temp_path)
        self.assertFalse(default_storage.exists(temp_path))

    def test_cancel_deletes_temp_image(self):
        """test that cancelling deletes temporary image"""
        uploaded_file = create_test_image()

        data = self.form_data.copy()
        data["image"] = uploaded_file

        self.client.post(self.url, data, format="multipart", follow=True)

        session = self.client.session
        temp_path = session.get("recipe_form_data", {}).get("temp_image_path")

        self.client.get(reverse("cancel_recipe"))

        if temp_path:
            self.assertFalse(default_storage.exists(temp_path))
