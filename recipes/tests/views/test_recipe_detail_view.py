from django.test import TestCase
from django.urls import reverse
from recipes.models import Recipe, User
from django.utils import timezone 

class RecipeDetailViewTestCase(TestCase):
    """Tests for the recipe detail view."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.client.login(username='@johndoe', password='Password123')

        self.recipe = Recipe.objects.create(
            author=self.user,
            title="Korean Noodles",
            adjectives="quick easy",
            publication_date=timezone.now().date(),
            ingredients="test (1)",
            steps="test"
        )
        self.url = reverse('recipe_detail', kwargs={'recipe_id': self.recipe.id})

    def test_recipe_detail_url(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
    
    def test_recipe_detail_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'recipe.html')

    def test_recipe_detail_context(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context['recipe'], self.recipe)

    def test_invalid_recipe_id_returns_404(self):
        url = reverse('recipe_detail', kwargs={'recipe_id': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_recipe_detail_with_negative_id(self):
        response = self.client.get("/recipe/-1")
        self.assertEqual(response.status_code, 404)

    def test_recipe_detail_with_zero_id(self):
        response = self.client.get("/recipe/0")
        self.assertEqual(response.status_code, 404)

    def test_recipe_detail_with_very_large_id(self):
        response = self.client.get("/recipe/999999999")
        self.assertEqual(response.status_code, 404)

    def test_recipe_detail_displays_title(self):
        """Test that recipe title is displayed on the page"""
        response = self.client.get(self.url)
        self.assertContains(response, "Korean Noodles")
    
    def test_recipe_detail_displays_adjectives(self):
        """Test that recipe adjectives are displayed on the page"""
        response = self.client.get(self.url)
        self.assertContains(response, "quick easy")
        self.assertContains(response, self.recipe.adjectives)

    def test_recipe_detail_displays_ingredients(self):
        """Test that recipe ingredients are displayed on the page"""
        response = self.client.get(self.url)
        self.assertContains(response, "test (1)")
        self.assertContains(response, self.recipe.ingredients)

    def test_recipe_detail_displays_steps(self):
        """Test that recipe steps are displayed on the page"""
        response = self.client.get(self.url)
        self.assertContains(response, "test")
        self.assertContains(response, self.recipe.steps)
    
    def test_recipe_detail_displays_author(self):
        """Test that recipe author username is displayed"""
        response = self.client.get(self.url)
        self.assertContains(response, self.user.username)
    
    def test_recipe_detail_displays_publication_date(self):
        """Test that publication date is displayed"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        # Check that the formatted date appears
        formatted_date = self.recipe.publication_date.strftime('%b. %-d, %Y')
        self.assertContains(response, formatted_date)
    
    def test_recipe_detail_with_long_title(self):
        """Test displaying recipe with maximum length title"""
        long_title = "A" * 255
        recipe = Recipe.objects.create(
            author=self.user,
            title=long_title,
            adjectives="test",
            publication_date=timezone.now().date()
        )
        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, long_title)
    
    def test_recipe_detail_with_minimum_length_title(self):
        """Test displaying recipe with minimum valid title (4 chars)"""
        recipe = Recipe.objects.create(
            author=self.user,
            title="ABCD",
            adjectives="test",
            publication_date=timezone.now().date()
        )
        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ABCD")
    
    def test_recipe_detail_with_special_characters(self):
        """Test displaying recipe with special characters in title"""
        recipe = Recipe.objects.create(
            author=self.user,
            title="Grandmother's Secret Recipe! (The Best)",
            adjectives="special",
            publication_date=timezone.now().date()
        )
        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Grandmother&#x27;s Secret Recipe! (The Best)")
    
    def test_recipe_detail_from_different_author(self):
        """Test viewing recipe created by a different user"""
        try:
            other_user = User.objects.get(username='@janedoe')
        except User.DoesNotExist:
            other_user = User.objects.create_user(
                username='@janedoe',
                email='jane@example.com',
                password='Password123'
            )
        other_recipe = Recipe.objects.create(
            author=other_user,
            title="Jane's Recipe",
            adjectives="collaborative",
            publication_date=timezone.now().date()
        )
        url = reverse('recipe_detail', kwargs={'recipe_id': other_recipe.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Jane&#x27;s Recipe")
        self.assertContains(response, other_user.username)

    def test_recipe_detail_displays_image_when_present(self):
        """Test that recipe image is displayed when recipe has an image"""
        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image
        from io import BytesIO

        # Create a real image
        image = Image.new('RGB', (100, 100), color='blue')
        image_file = BytesIO()
        image.save(image_file, 'JPEG')
        image_file.seek(0)

        # Create recipe with image
        recipe_with_image = Recipe.objects.create(
            author=self.user,
            title="Recipe with Image",
            adjectives="visual tasty",
            publication_date=timezone.now().date(),
            servings=4,
            ingredients="Tomato (2)",
            steps="Cook it",
            image=SimpleUploadedFile('test.jpg', image_file.read(),content_type='image/jpeg')
        )

        url = reverse('recipe_detail', kwargs={'recipe_id': recipe_with_image.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        # Check that image tag is present
        self.assertContains(response, '<img')
        self.assertContains(response, recipe_with_image.image.url)

    def test_recipe_detail_without_image_shows_no_image_tag(self):
        """Test that no image tag appears when recipe has no image"""
        recipe_without_image = Recipe.objects.create(
            author=self.user,
            title="Recipe without Image",
            adjectives="simple quick",
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
        """Test that recipe servings are displayed"""
        recipe = Recipe.objects.create(
            author=self.user,
            title="Four Serving Recipe",
            adjectives="family sized",
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
        """Test that servings adjustment form is present"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        # Check for servings input field
        self.assertContains(response, 'name="servings"')
        self.assertContains(response, 'Adjust Servings')
        self.assertContains(response, 'Recalculate')

    def test_recipe_detail_with_minimum_servings(self):
        """Test recipe with minimum servings (1)"""
        recipe = Recipe.objects.create(
            author=self.user,
            title="Single Serving Recipe",
            adjectives="solo meal",
            publication_date=timezone.now().date(),
            servings=1,
            ingredients="Egg (1)",
            steps="Fry egg"
        )

        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "1")
        self.assertContains(response, "serving")

    def test_recipe_detail_with_large_servings(self):
        """Test recipe with large number of servings"""
        recipe = Recipe.objects.create(
            author=self.user,
            title="Party Recipe",
            adjectives="crowd pleaser",
            publication_date=timezone.now().date(),
            servings=50,
            ingredients="Chicken (10kg)",
            steps="Cook for party"
        )

        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "50")

    def test_servings_scaling_doubles_ingredients(self):
          """Test that doubling servings doubles ingredient quantities"""
          recipe = Recipe.objects.create(
              author=self.user,
              title="Scalable Recipe",
              adjectives="flexible portions",
              publication_date=timezone.now().date(),
              servings=2,
              ingredients="Sugar (100g)\nFlour (200g)",
              steps="Mix ingredients"
          )

          url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
          # Request with 4 servings (double the original 2)
          response = self.client.get(url, {'servings': 4})

          self.assertEqual(response.status_code, 200)
          # Check that quantities are doubled
          self.assertContains(response, "200")  # Sugar doubled from 100g
          self.assertContains(response, "400")  # Flour doubled from 200g

    def test_servings_scaling_halves_ingredients(self):
        """Test that halving servings halves ingredient quantities"""
        recipe = Recipe.objects.create(
            author=self.user,
            title="Halvable Recipe",
            adjectives="adjustable",
            publication_date=timezone.now().date(),
            servings=4,
            ingredients="Butter (200g)\nMilk (400ml)",
            steps="Mix ingredients"
        )

        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        # Request with 2 servings (half the original 4)
        response = self.client.get(url, {'servings': 2})

        self.assertEqual(response.status_code, 200)
        # Check that quantities are halved
        self.assertContains(response, "100")  # Butter halved from 200g
        self.assertContains(response, "200")  # Milk halved from 400ml

    def test_servings_with_invalid_value_uses_default(self):
        """Test that invalid servings value falls back to recipe default"""
        recipe = Recipe.objects.create(
            author=self.user,
            title="Default Servings Recipe",
            adjectives="stable",
            publication_date=timezone.now().date(),
            servings=3,
            ingredients="Rice (300g)",
            steps="Cook rice"
        )

        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        # Request with invalid servings
        response = self.client.get(url, {'servings': 'invalid'})

        self.assertEqual(response.status_code, 200)
        # Should use original 3 servings, so rice stays at 300g
        self.assertContains(response, "300")
        self.assertContains(response, "3")

    def test_servings_with_empty_value_uses_default(self):
        """Test that empty servings value falls back to recipe default"""
        recipe = Recipe.objects.create(
            author=self.user,
            title="Empty Servings Test",
            adjectives="default fallback",
            publication_date=timezone.now().date(),
            servings=5,
            ingredients="Pasta (500g)",
            steps="Boil pasta"
        )

        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        # Request with empty servings
        response = self.client.get(url, {'servings': ''})

        self.assertEqual(response.status_code, 200)
        # Should use original 5 servings
        self.assertContains(response, "500")
        self.assertContains(response, "5")

    def test_servings_scaling_factor_displayed(self):
        """Test that scaling factor is displayed when servings are adjusted"""
        recipe = Recipe.objects.create(
            author=self.user,
            title="Scaling Display Test",
            adjectives="informative",
            publication_date=timezone.now().date(),
            servings=2,
            ingredients="Salt (2g)",
            steps="Add salt"
        )

        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        # Request with 6 servings (3x the original)
        response = self.client.get(url, {'servings': 6})

        self.assertEqual(response.status_code, 200)
        # Check that scaling factor message appears
        self.assertContains(response, "scaled by")
        self.assertContains(response, "3.00")  # 6/2 = 3

    def test_recipe_with_multiple_ingredients(self):
        """Test recipe with multiple ingredients displays all correctly"""
        recipe = Recipe.objects.create(
            author=self.user,
            title="Complex Recipe",
            adjectives="detailed",
            publication_date=timezone.now().date(),
            servings=4,
            ingredients="Flour (500g)\nSugar (200g)\nEggs (3)\nMilk (250ml)\nButter (100g)",
            steps="Mix everything"
        )

        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        # Check all ingredients are present
        self.assertContains(response, "Flour")
        self.assertContains(response, "500g")
        self.assertContains(response, "Sugar")
        self.assertContains(response, "200g")
        self.assertContains(response, "Eggs")
        self.assertContains(response, "Milk")
        self.assertContains(response, "Butter")

    def test_recipe_with_multiple_steps(self):
        """Test recipe with multiple steps displays all in order"""
        recipe = Recipe.objects.create(
            author=self.user,
            title="Multi-Step Recipe",
            adjectives="sequential",
            publication_date=timezone.now().date(),
            servings=2,
            ingredients="Water (1L)",
            steps="Boil water\nAdd salt\nReduce heat\nSimmer for 10 minutes\nServe hot"
        )

        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        # Check all steps are present
        self.assertContains(response, "Boil water")
        self.assertContains(response, "Add salt")
        self.assertContains(response, "Reduce heat")
        self.assertContains(response, "Simmer for 10 minutes")
        self.assertContains(response, "Serve hot")

    def test_recipe_detail_has_update_button(self):
        """Test that update button is present"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Update this recipe')
        update_url = reverse('update_recipe', kwargs={'recipe_id': self.recipe.id})
        self.assertContains(response, update_url)

    def test_recipe_detail_has_delete_button(self):
        """Test that delete button is present"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Delete this recipe')
        delete_url = reverse('delete_recipe', kwargs={'recipe_id': self.recipe.id})
        self.assertContains(response, delete_url)

    def test_recipe_detail_has_back_button(self):
        """Test that back to home button is present"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Go back home')
        home_url = reverse('home')
        self.assertContains(response, home_url)
