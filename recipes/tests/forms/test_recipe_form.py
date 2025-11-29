from django.test import TestCase
from recipes.forms.recipe_form import RecipeForm
from recipes.models import User
from django.utils import timezone
from datetime import timedelta
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from io import BytesIO


class RecipeFormTestCase(TestCase):
    # Tests for the RecipeForm

    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.client.login(username='@johndoe', password='Password123')
        self.form_data = {
            'title': 'Test Recipe',
            'publication_date': timezone.now().date(),
            'servings': 4,
            'ingredients': "test (1)",
            'steps': "test",
            'prep_time_hours': 0,
            'prep_time_minutes': 30,
            'cook_time_hours': 1,
            'cook_time_minutes': 15,
            'private': False,
        }

    # Helper: assert form is valid with given field overrides
    def _assert_form_valid(self, **kwargs):
        data = {**self.form_data, **kwargs}
        form = RecipeForm(data=data)
        if not form.is_valid():
            print(f"Form errors: {form.errors}")
        self.assertTrue(form.is_valid())

    # Helper: assert form is invalid and field has error
    def _assert_form_invalid(self, field, **kwargs):
        data = {**self.form_data, **kwargs}
        form = RecipeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn(field, form.errors)
        return form.errors[field]

    # Test form is valid with correct data
    def test_valid_form(self):
        self._assert_form_valid()

    # Test form has all required fields
    def test_form_has_necessary_fields(self):
        form = RecipeForm()
        expected_fields = ['title', 'publication_date', 'servings', 'ingredients', 
                          'steps', 'prep_time_hours', 'prep_time_minutes', 
                          'cook_time_hours', 'cook_time_minutes']
        for field in expected_fields:
            self.assertIn(field, form.fields)

    # Test blank title is rejected
    def test_form_rejects_blank_title(self):
        self._assert_form_invalid('title', title='')

    # Test title less than 4 characters is rejected
    def test_form_rejects_short_title(self):
        self._assert_form_invalid('title', title='Hi')

    # Test title with exactly 4 characters is accepted
    def test_form_accepts_minimum_length_title(self):
        self._assert_form_valid(title='Test')

    # Title with 255 characters is accepted
    def test_form_accepts_maximum_length_title(self):
        self._assert_form_valid(title='A' * 255)

    # Test title is longer than 255 characters is rejected
    def test_form_rejects_title_exceeding_max_length(self):
        self._assert_form_invalid('title', title='A' * 256)

    # Test blank servings is rejected
    def test_form_rejects_blank_servings(self):
        self._assert_form_invalid('servings', servings='')

    # Test zero servings is rejected
    def test_form_rejects_zero_servings(self):
        self._assert_form_invalid('servings', servings=0)

    # Test negative servings is rejected
    def test_form_rejects_negative_servings(self):
        self._assert_form_invalid('servings', servings=-5)

    # Test servings = 1 is accepted
    def test_form_accepts_minimum_servings(self):
        self._assert_form_valid(servings=1)

    # Test large servings number is accepted
    def test_form_accepts_large_servings(self):
        self._assert_form_valid(servings=100)

    # Test future publication date is rejected
    def test_form_rejects_future_publication_date(self):
        future = timezone.now().date() + timedelta(days=1)
        errors = self._assert_form_invalid('publication_date', publication_date=future)
        self.assertIn('cannot be in the future', str(errors))

    # Test today's date is accepted
    def test_form_accepts_today_as_publication_date(self):
        self._assert_form_valid(publication_date=timezone.now().date())

    # Test past date is accepted
    def test_form_accepts_past_publication_date(self):
        past = timezone.now().date() - timedelta(days=7)
        self._assert_form_valid(publication_date=past)

    # Test blank ingredients is rejected
    def test_form_rejects_blank_ingredients(self):
        self._assert_form_invalid('ingredients', ingredients='')

    # Test ingredients without parentheses are rejected
    def test_form_rejects_ingredient_without_parentheses(self):
        errors = self._assert_form_invalid('ingredients', ingredients='Flour 500g')
        self.assertIn('parentheses', str(errors).lower())

    # Test text after closing parenthesis is rejected
    def test_form_rejects_ingredient_with_text_after_parentheses(self):
        self._assert_form_invalid('ingredients', ingredients='Avocado (1) piece')

    # Test multiple sets of parentheses are rejected
    def test_form_rejects_ingredient_with_multiple_parentheses(self):
        self._assert_form_invalid('ingredients', ingredients='Sugar (white) (100g)')

    # Test properly formatted ingredient is accepted
    def test_form_accepts_valid_ingredient_format(self):
        self._assert_form_valid(ingredients='Flour (500g)')

    # Test multiple properly formatted ingredients are accepted
    def test_form_accepts_multiple_valid_ingredients(self):
        self._assert_form_valid(ingredients='Flour (500g)\nSugar (200g)\nEggs (3)')

    # Test form rejects if any ingredient is invalid
    def test_form_rejects_mixed_valid_and_invalid_ingredients(self):
        errors = self._assert_form_invalid('ingredients', 
            ingredients='Flour (500g)\nSugar 200g\nEggs (3)')
        self.assertIn('Line 2', str(errors))

    # Ingredient names with spaces are accepted
    def test_form_accepts_ingredient_with_spaces_in_name(self):
        self._assert_form_valid(ingredients='Chicken breast (500g)')

    # Complex quantities in parentheses are accepted
    # This fails, do we need it to pass?
    def test_form_accepts_ingredient_with_complex_quantity(self):
        self._assert_form_valid(ingredients='Milk (2 cups or 500ml)')

    # Error messages are helpful and specific
    def test_form_provides_helpful_error_for_invalid_ingredients(self):
        errors = self._assert_form_invalid('ingredients', 
            ingredients='Salt\nPepper (1 tsp)\nGarlic')
        error_msg = str(errors)
        self.assertIn('Line 1', error_msg)
        self.assertIn('Line 3', error_msg)
        self.assertIn('Ingredient name (quantity)', error_msg)

    # Empty lines in ingredients are handled
    def test_form_with_empty_lines_in_ingredients(self):
        self._assert_form_valid(ingredients='Flour (500g)\n\nSugar (200g)\n\n')

    # Zero prep and cook time is accepted
    def test_form_accepts_zero_prep_and_cook_time(self):
        self._assert_form_valid(prep_time_hours=0, prep_time_minutes=0,
                               cook_time_hours=0, cook_time_minutes=0)

    # Valid time values are accepted
    def test_form_accepts_valid_time_values(self):
        self._assert_form_valid(prep_time_hours=2, prep_time_minutes=30,
                               cook_time_hours=1, cook_time_minutes=45)

    # Negative time values are rejected
    def test_form_rejects_negative_time_values(self):
        self._assert_form_invalid('prep_time_hours', prep_time_hours=-1)
        self._assert_form_invalid('prep_time_minutes', prep_time_minutes=-5)
        self._assert_form_invalid('cook_time_hours', cook_time_hours=-2)
        self._assert_form_invalid('cook_time_minutes', cook_time_minutes=-10)

    # Minutes over 59 are rejected
    def test_form_rejects_minutes_over_59(self):
        self._assert_form_invalid('prep_time_minutes', prep_time_minutes=60)
        self._assert_form_invalid('cook_time_minutes', cook_time_minutes=75)

    # Minutes at exactly 59 are accepted
    def test_form_accepts_minutes_at_59(self):
        self._assert_form_valid(prep_time_minutes=59, cook_time_minutes=59)

    # Large but valid time values are accepted
    def test_form_accepts_large_time_values(self):
        self._assert_form_valid(prep_time_hours=10, cook_time_hours=8)

    # String values in time fields are rejected
    def test_form_rejects_string_in_time_fields(self):
        self._assert_form_invalid('prep_time_hours', prep_time_hours='two')
        self._assert_form_invalid('prep_time_minutes', prep_time_minutes='thirty')
        self._assert_form_invalid('cook_time_hours', cook_time_hours='one')
        self._assert_form_invalid('cook_time_minutes', cook_time_minutes='fifteen')

    # Decimal values in time fields are rejected
    def test_form_rejects_decimal_in_time_fields(self):
        self._assert_form_invalid('prep_time_hours', prep_time_hours=1.5)

    # Image field is optional
    def test_form_accepts_optional_image(self):
        self._assert_form_valid()

    # Valid image file is accepted
    def test_form_accepts_valid_image(self):
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

    # Special characters are handled correctly
    def test_form_with_special_characters_in_fields(self):
        self._assert_form_valid(
            title="Chef's Special: 'Delicious!' Recipe",
            ingredients="Chef's secret ingredient (1 tsp)"
        )

    # Empty lines in steps are handled
    def test_form_with_empty_lines_in_steps(self):
        self._assert_form_valid(steps='Mix flour\n\nAdd sugar\n\n')

    # Form saves data correctly
    def test_form_saves_correctly(self):
        form = RecipeForm(data=self.form_data)
        self.assertTrue(form.is_valid())
        recipe = form.save(commit=False)
        recipe.author = self.user
        recipe.save()
        
        self.assertEqual(recipe.title, 'Test Recipe')
        self.assertEqual(recipe.author, self.user)
        self.assertEqual(recipe.servings, 4)
        self.assertEqual(recipe.ingredients, 'test (1)')
        self.assertEqual(recipe.steps, 'test')