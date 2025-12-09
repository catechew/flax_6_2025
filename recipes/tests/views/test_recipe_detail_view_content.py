from django.test import TestCase
from django.urls import reverse
from recipes.models import Recipe, User
from django.utils import timezone 
from unittest.mock import patch

class RecipeDetailViewTestCase(TestCase):
    """
    Tests for the recipe detail view.
    """

    fixtures = [
        'recipes/tests/fixtures/default_user.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.client.login(username='@johndoe', password='Password123')

        self.recipe = Recipe.objects.create(
            author=self.user,
            title="Korean Noodles",                        
            publication_date=timezone.now().date(),
            ingredients="test (1)",
            steps="test"
        )
        self.url = reverse('recipe_detail', kwargs={'recipe_id': self.recipe.id})

    def test_recipe_detail_with_long_title(self):
        """ Test displaying recipe with maximum length title. """
        long_title = "A" * 255
        recipe = Recipe.objects.create(
            author=self.user,
            title=long_title,
            publication_date=timezone.now().date()
        )
        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, long_title)
    
    def test_recipe_detail_with_minimum_length_title(self):
        """ Test displaying recipe with minimum valid title (4 chars). """
        recipe = Recipe.objects.create(
            author=self.user,
            title="ABCD",
            publication_date=timezone.now().date()
        )
        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ABCD")
    
    def test_recipe_detail_with_special_characters(self):
        """ Test displaying recipe with special characters in title. """
        recipe = Recipe.objects.create(
            author=self.user,
            title="Grandmother's Secret Recipe! (The Best)",
            publication_date=timezone.now().date()
        )
        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Grandmother&#x27;s Secret Recipe! (The Best)")
    
    def test_recipe_detail_from_different_author(self):
        """ Test viewing recipe created by a different user. """
        other_user, created = User.objects.get_or_create(
            username='@janedoe',
            defaults={
                'email': 'jane@example.com',
                'password': 'Password123'
            }
        )
        other_recipe = Recipe.objects.create(
            author=other_user,
            title="Jane's Recipe",
            publication_date=timezone.now().date()
        )
        url = reverse('recipe_detail', kwargs={'recipe_id': other_recipe.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Jane&#x27;s Recipe")
        self.assertContains(response, other_user.username)

    def test_recipe_detail_displays_image_when_present(self):
        """ Test that recipe image is displayed when recipe has an image. """
        recipe_with_image = self._create_recipe_with_image()
        url = reverse('recipe_detail', kwargs={'recipe_id': recipe_with_image.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<img')
        self.assertContains(response, recipe_with_image.image.url)

    def _create_test_image(self):
        """ Create a test image file for upload. """
        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image
        from io import BytesIO

        image = Image.new('RGB', (100, 100), color='blue')
        image_file = BytesIO()
        image.save(image_file, 'JPEG')
        image_file.seek(0)
    
        return SimpleUploadedFile('test.jpg', image_file.read(), content_type='image/jpeg')

    def _create_recipe_with_image(self):
        """ Create a recipe with an attached image. """
        return Recipe.objects.create(
            author=self.user,
            title="Recipe with Image",
            publication_date=timezone.now().date(),
            servings=4,
            ingredients="Tomato (2)",
            steps="Cook it",
            image=self._create_test_image()
        )

    def test_recipe_detail_without_image_shows_no_image_tag(self):
        """ Test that no image tag appears when recipe has no image. """
        recipe_without_image = Recipe.objects.create(
            author=self.user,
            title="Recipe without Image",
            publication_date=timezone.now().date(),
            servings=2,
            ingredients="Salt (1 pinch)",
            steps="Add salt"
        )
        url = reverse('recipe_detail', kwargs={'recipe_id': recipe_without_image.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        # The recipe title should be there, but image-related tags should not
        self.assertContains(response, "Recipe without Image")
        # Check that the img tag for recipe.image.url is not present
        self.assertNotContains(response, 'recipe_images/')
    
    def test_recipe_detail_displays_servings(self):
        """ Test that recipe servings are displayed. """
        recipe = Recipe.objects.create(
            author=self.user,
            title="Four Serving Recipe",
            publication_date=timezone.now().date(),
            servings=4,
            ingredients="Pasta (500g)",
            steps="Boil pasta"
        )

        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "4")
        self.assertContains(response, "servings")

    def test_recipe_detail_servings_adjustment_form(self):
        """ Test that servings adjustment form is present. """
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        # Check for servings input field
        self.assertContains(response, 'name="servings"')
        self.assertContains(response, 'Adjust Servings')
        self.assertContains(response, 'Recalculate')
