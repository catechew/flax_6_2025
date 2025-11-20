from django.test import TestCase
from recipes.forms.recipe_form import RecipeForm
from recipes.models import User
from django.utils import timezone
from datetime import timedelta

class RecipeFormTestCase(TestCase):
    """Tests for the RecipeForm"""

    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.client.login(username='@johndoe', password='Password123')
        self.form_data = {
            'title': 'Test Recipe',
            'adjectives': 'quick easy',
            'publication_date': timezone.now().date(),
            'servings' : 4,
            'ingredients' : "test (1)",
            'steps' : "test"
        }

    # Test that form is valid with correct data
    def test_valid_form(self):
        form = RecipeForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    # Test that form has all necessary fields
    def test_form_has_necessary_fields(self):
        form = RecipeForm()
        self.assertIn('title', form.fields)
        self.assertIn('adjectives', form.fields)
        self.assertIn('publication_date', form.fields)
        self.assertIn('servings', form.fields)
        self.assertIn('ingredients', form.fields)
        self.assertIn('steps', form.fields)

    # Test that form rejects blank title
    def test_form_rejects_blank_title(self):
        self.form_data['title'] = ''
        form = RecipeForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    # Test that form rejects blank adjectives
    def test_form_rejects_blank_adjectives(self):
        self.form_data['adjectives'] = ''
        form = RecipeForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('adjectives', form.errors)

    # Test that form rejects blank servings
    def test_form_rejects_blank_servings(self):
        self.form_data['servings'] = ''
        form = RecipeForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('servings', form.errors)

    # Test that form rejects blank ingredients
    def test_form_rejects_blank_ingredients(self):
        self.form_data['ingredients'] = ''
        form = RecipeForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('ingredients', form.errors)
    
    # Test that form rejects blank steps
    def test_form_rejects_blank_adjectives(self):
        self.form_data['steps'] = ''
        form = RecipeForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('steps', form.errors)

    # Test that form rejects title less than 4 characters
    def test_form_rejects_short_title(self):
        self.form_data['title'] = 'Hi'
        form = RecipeForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    # Test that form rejects adjectives less than 4 characters
    def test_form_rejects_short_adjectives(self):
        self.form_data['adjectives'] = 'ok'
        form = RecipeForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('adjectives', form.errors)

    # Test that form accepts title with exactly 4 characters
    def test_form_accepts_minimum_length_title(self):
        self.form_data['title'] = 'Test'
        form = RecipeForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    # Test that form accepts adjectives with exactly 4 characters
    def test_form_accepts_minimum_length_adjectives(self):
        self.form_data['adjectives'] = 'fast'
        form = RecipeForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    # Test that form saves data correctly
    def test_form_saves_correctly(self):
        form = RecipeForm(data=self.form_data)
        self.assertTrue(form.is_valid())
        recipe = form.save(commit=False)
        recipe.author=self.user
        recipe.save()
        self.assertEqual(recipe.title, 'Test Recipe')
        self.assertEqual(recipe.adjectives, 'quick easy')
        self.assertEqual(recipe.author, self.user)
        self.assertEqual(recipe.servings, 4)
        self.assertEqual(recipe.ingredients, 'test (1)')
        self.assertEqual(recipe.steps, 'test')

    # Test that form rejects future publication date
    def test_form_rejects_future_publication_date(self):
          future_date = timezone.now().date() + timedelta(days=1)
          self.form_data['publication_date'] = future_date
          form = RecipeForm(data=self.form_data)
          self.assertFalse(form.is_valid())
          self.assertIn('publication_date', form.errors)
          self.assertIn('cannot be in the future', str(form.errors['publication_date']))

    # Test that form rejects publication date far in the future
    def test_form_rejects_far_future_publication_date(self):
        future_date = timezone.now().date() + timedelta(days=365)
        self.form_data['publication_date'] = future_date
        form = RecipeForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('publication_date', form.errors)

    # Test that form accepts today's date as publication date
    def test_form_accepts_today_as_publication_date(self):
        self.form_data['publication_date'] = timezone.now().date()
        form = RecipeForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    # Test that form accepts past publication date
    def test_form_accepts_past_publication_date(self):
        past_date = timezone.now().date() - timedelta(days=7)
        self.form_data['publication_date'] = past_date
        form = RecipeForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    # Test that form accepts yesterday's date as publication date
    def test_form_accepts_yesterday_as_publication_date(self):
        yesterday = timezone.now().date() - timedelta(days=1)
        self.form_data['publication_date'] = yesterday
        form = RecipeForm(data=self.form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_rejects_zero_servings(self):
        """Test that form rejects servings = 0"""
        self.form_data['servings'] = 0
        form = RecipeForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('servings', form.errors)

    def test_form_rejects_negative_servings(self):
        """Test that form rejects negative servings"""
        self.form_data['servings'] = -5
        form = RecipeForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('servings', form.errors)

    def test_form_accepts_minimum_servings(self):
        """Test that form accepts servings = 1"""
        self.form_data['servings'] = 1
        form = RecipeForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_form_accepts_large_servings(self):
        """Test that form accepts large number of servings"""
        self.form_data['servings'] = 100
        form = RecipeForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_form_rejects_ingredient_without_parentheses(self):
        """Test that ingredients without parentheses are rejected"""
        self.form_data['ingredients'] = 'Flour 500g'
        form = RecipeForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('ingredients', form.errors)
        self.assertIn('parentheses', str(form.errors['ingredients']).lower())

    def test_form_rejects_ingredient_with_text_after_parentheses(self):
        """Test that ingredients with text after closing parenthesis are rejected"""
        self.form_data['ingredients'] = 'Avocado (1) piece'
        form = RecipeForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('ingredients', form.errors)

    def test_form_rejects_ingredient_with_multiple_parentheses(self):
        """Test that ingredients with multiple sets of parentheses are rejected"""
        self.form_data['ingredients'] = 'Sugar (white) (100g)'
        form = RecipeForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('ingredients', form.errors)

    def test_form_accepts_valid_ingredient_format(self):
        """Test that properly formatted ingredients are accepted"""
        self.form_data['ingredients'] = 'Flour (500g)'
        form = RecipeForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_form_accepts_multiple_valid_ingredients(self):
        """Test that multiple properly formatted ingredients are accepted"""
        self.form_data['ingredients'] = 'Flour (500g)\nSugar (200g)\nEggs (3)'
        form = RecipeForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_form_rejects_mixed_valid_and_invalid_ingredients(self):
        """Test that form rejects if any ingredient is invalid"""
        self.form_data['ingredients'] = 'Flour (500g)\nSugar 200g\nEggs (3)'
        form = RecipeForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('ingredients', form.errors)
        # Should mention line 2 has the error
        self.assertIn('Line 2', str(form.errors['ingredients']))

    def test_form_accepts_ingredient_with_spaces_in_name(self):
        """Test that ingredient names with spaces are accepted"""
        self.form_data['ingredients'] = 'Chicken breast (500g)'
        form = RecipeForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_form_accepts_ingredient_with_complex_quantity(self):
        """Test that complex quantities in parentheses are accepted"""
        self.form_data['ingredients'] = 'Milk (2 cups or 500ml)'
        form = RecipeForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_form_provides_helpful_error_for_invalid_ingredients(self):
        """Test that error messages are helpful and specific"""
        self.form_data['ingredients'] = 'Salt\nPepper (1 tsp)\nGarlic'
        form = RecipeForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        error_message = str(form.errors['ingredients'])
        # Should mention both problematic lines
        self.assertIn('Line 1', error_message)
        self.assertIn('Line 3', error_message)
        # Should include the correct format example
        self.assertIn('Ingredient name (quantity)', error_message)
    
    def test_form_accepts_optional_image(self):
        """Test that image field is optional"""
        # Don't include image in form_data
        form = RecipeForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_form_accepts_valid_image(self):
        """Test that form accepts valid image file"""
        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image
        from io import BytesIO

        # Create a real image
        image = Image.new('RGB', (100, 100), color='red')
        image_file = BytesIO()
        image.save(image_file, 'JPEG')
        image_file.seek(0)

        uploaded_file = SimpleUploadedFile(
            name='test.jpg',
            content=image_file.read(),
            content_type='image/jpeg'
        )

        form = RecipeForm(data=self.form_data, files={'image': uploaded_file})
        self.assertTrue(form.is_valid())
    
    def test_form_with_maximum_length_title(self):
        """Test form with maximum length title (255 chars)"""
        self.form_data['title'] = 'A' * 255
        form = RecipeForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_form_rejects_title_exceeding_max_length(self):
        """Test that title longer than 255 chars is rejected"""
        self.form_data['title'] = 'A' * 256
        form = RecipeForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_form_with_special_characters_in_fields(self):
        """Test that special characters are handled correctly"""
        self.form_data['title'] = "Chef's Special: 'Delicious!' Recipe"
        self.form_data['adjectives'] = 'unique & tasty!'
        self.form_data['ingredients'] = "Chef's secret ingredient (1 tsp)"
        form = RecipeForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_form_with_empty_lines_in_ingredients(self):
        """Test that empty lines in ingredients are handled"""
        self.form_data['ingredients'] = 'Flour (500g)\n\nSugar (200g)\n\n'
        form = RecipeForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_form_with_empty_lines_in_steps(self):
        """Test that empty lines in steps are handled"""
        self.form_data['steps'] = 'Mix flour\n\nAdd sugar\n\n'
        form = RecipeForm(data=self.form_data)
        self.assertTrue(form.is_valid())
