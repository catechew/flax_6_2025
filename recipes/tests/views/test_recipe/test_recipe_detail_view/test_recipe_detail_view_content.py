from django.urls import reverse
from recipes.tests.views.test_helpers_base import BaseRecipeViewTestCase

"""
Tests for the recipe detail view - content display.
"""


class RecipeDetailViewContentTests(BaseRecipeViewTestCase):

    def setUp(self):
        super().setUp()
        self.recipe = self.create_test_recipe(title="Korean Noodles")
        self.url = reverse("recipe_detail", kwargs={"recipe_id": self.recipe.id})

    def test_recipe_detail_with_long_title(self):
        """Test displaying recipe with maximum length title."""
        long_title = "A" * 255
        recipe = self.create_test_recipe(title=long_title)
        url = reverse("recipe_detail", kwargs={"recipe_id": recipe.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, long_title)

    def test_recipe_detail_with_minimum_length_title(self):
        """Test displaying recipe with minimum valid title (4 chars)."""
        recipe = self.create_test_recipe(title="ABCD")
        url = reverse("recipe_detail", kwargs={"recipe_id": recipe.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ABCD")

    def test_recipe_detail_with_special_characters(self):
        """Test displaying recipe with special characters in title."""
        recipe = self.create_test_recipe(
            title="Grandmother's Secret Recipe! (The Best)"
        )
        url = reverse("recipe_detail", kwargs={"recipe_id": recipe.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Grandmother&#x27;s Secret Recipe! (The Best)")

    def test_recipe_detail_from_different_author(self):
        """Test viewing recipe created by a different user."""
        from recipes.models import User

        other_user, created = User.objects.get_or_create(
            username="@janedoe",
            defaults={"email": "jane@example.com", "password": "Password123"},
        )
        other_recipe = self.create_test_recipe(author=other_user, title="Jane's Recipe")
        url = reverse("recipe_detail", kwargs={"recipe_id": other_recipe.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Jane&#x27;s Recipe")
        self.assertContains(response, other_user.username)

    def test_recipe_detail_displays_image_when_present(self):
        """Test that recipe image is displayed when recipe has an image."""
        recipe_with_image = self._create_recipe_with_image()
        url = reverse("recipe_detail", kwargs={"recipe_id": recipe_with_image.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<img")
        self.assertContains(response, recipe_with_image.image.url)

    def _create_test_image(self):
        """Create a test image file for upload."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image
        from io import BytesIO

        image = Image.new("RGB", (100, 100), color="blue")
        image_file = BytesIO()
        image.save(image_file, "JPEG")
        image_file.seek(0)

        return SimpleUploadedFile(
            "test.jpg", image_file.read(), content_type="image/jpeg"
        )

    def _create_recipe_with_image(self):
        """Create a recipe with an attached image."""
        return self.create_test_recipe(
            title="Recipe with Image",
            servings=4,
            ingredients="Tomato (2)",
            steps="Cook it",
            image=self._create_test_image(),
        )

    def test_recipe_detail_without_image_shows_no_image_tag(self):
        """Test that no image tag appears when recipe has no image."""
        recipe_without_image = self.create_test_recipe(
            title="Recipe without Image",
            servings=2,
            ingredients="Salt (1 pinch)",
            steps="Add salt",
        )
        url = reverse("recipe_detail", kwargs={"recipe_id": recipe_without_image.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Recipe without Image")
        self.assertNotContains(response, "recipe_images/")

    def test_recipe_detail_displays_servings(self):
        """Test that recipe servings are displayed."""
        recipe = self.create_test_recipe(
            title="Four Serving Recipe",
            servings=4,
            ingredients="Pasta (500g)",
            steps="Boil pasta",
        )
        url = reverse("recipe_detail", kwargs={"recipe_id": recipe.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "4")
        self.assertContains(response, "servings")

    def test_recipe_detail_servings_adjustment_form(self):
        """Test that servings adjustment form is present."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="servings"')
        self.assertContains(response, "Adjust Servings")
        self.assertContains(response, "Recalculate")
