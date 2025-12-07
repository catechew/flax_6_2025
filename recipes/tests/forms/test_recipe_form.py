from django.test import TestCase
from django.core.exceptions import ValidationError
from recipes.forms.recipe_form import RecipeForm
from django.utils import timezone
from datetime import timedelta
from recipes.tests.utils import create_test_user, create_test_form_data, create_test_image


class RecipeFormTestCase(TestCase):
    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = create_test_user()
        self.form_data = create_test_form_data()

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

    def test_valid_form(self):
        self._assert_form_valid()

    def test_form_has_necessary_fields(self):
        form = RecipeForm()
        expected_fields = [
            'title', 'publication_date', 'servings', 'ingredients', 
            'steps', 'prep_time_hours', 'prep_time_minutes', 
            'cook_time_hours', 'cook_time_minutes'
        ]
        for field in expected_fields:
            self.assertIn(field, form.fields)

    def test_form_rejects_blank_title(self):
        self._assert_form_invalid('title', title='')

    def test_form_rejects_short_title(self):
        self._assert_form_invalid('title', title='Hi')

    def test_form_accepts_minimum_length_title(self):
        self._assert_form_valid(title='Test')

    def test_form_accepts_maximum_length_title(self):
        self._assert_form_valid(title='A' * 255)

    def test_form_rejects_title_exceeding_max_length(self):
        self._assert_form_invalid('title', title='A' * 256)

    def test_form_rejects_blank_servings(self):
        self._assert_form_invalid('servings', servings='')

    def test_form_rejects_zero_servings(self):
        self._assert_form_invalid('servings', servings=0)

    def test_form_rejects_negative_servings(self):
        self._assert_form_invalid('servings', servings=-5)

    def test_form_accepts_minimum_servings(self):
        self._assert_form_valid(servings=1)

    def test_form_accepts_large_servings(self):
        self._assert_form_valid(servings=100)

    def test_form_rejects_future_publication_date(self):
        future = timezone.now().date() + timedelta(days=1)
        errors = self._assert_form_invalid('publication_date', publication_date=future)
        self.assertIn('cannot be in the future', str(errors))

    def test_form_accepts_today_as_publication_date(self):
        self._assert_form_valid(publication_date=timezone.now().date())

    def test_form_accepts_past_publication_date(self):
        past = timezone.now().date() - timedelta(days=7)
        self._assert_form_valid(publication_date=past)

    def test_form_rejects_blank_ingredients(self):
        self._assert_form_invalid('ingredients', ingredients='')
        
    def test_form_rejects_whitespace_only_ingredients(self):
        errors = self._assert_form_invalid('ingredients', ingredients='   ')
        self.assertIn('required', str(errors).lower())
        
    def test_form_rejects_none_ingredients(self):
        """ Test form rejects None ingredients. """
        data = {**self.form_data, 'ingredients': None}
        form = RecipeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('ingredients', form.errors)

    def test_form_rejects_ingredient_with_unmatched_parenthesis_count(self):
        errors = self._assert_form_invalid('ingredients', 
            ingredients='Flour ((500g)')
        error_msg = str(errors)
        self.assertIn('Line 1', error_msg)
        self.assertIn('mismatched', error_msg.lower())

    def test_form_rejects_ingredient_without_parentheses(self):
        errors = self._assert_form_invalid('ingredients', ingredients='Flour 500g')
        self.assertIn('parentheses', str(errors).lower())

    def test_form_rejects_ingredient_with_text_after_parentheses(self):
        self._assert_form_invalid('ingredients', ingredients='Avocado (1) piece')

    def test_form_accepts_ingredient_with_multiple_parentheses(self):
        self._assert_form_valid(ingredients='Sugar (white) (100g)')

    def test_form_accepts_valid_ingredient_format(self):
        self._assert_form_valid(ingredients='Flour (500g)')

    def test_form_accepts_multiple_valid_ingredients(self):
        self._assert_form_valid(ingredients='Flour (500g)\nSugar (200g)\nEggs (3)')

    def test_form_rejects_mixed_valid_and_invalid_ingredients(self):
        errors = self._assert_form_invalid('ingredients', 
            ingredients='Flour (500g)\nSugar 200g\nEggs (3)')
        self.assertIn('Line 2', str(errors))

    def test_form_accepts_ingredient_with_spaces_in_name(self):
        self._assert_form_valid(ingredients='Chicken breast (500g)')

    def test_form_accepts_ingredient_with_complex_quantity(self):
        self._assert_form_valid(ingredients='Milk (2 cups or 500ml)')

    def test_form_provides_helpful_error_for_invalid_ingredients(self):
        errors = self._assert_form_invalid('ingredients', 
                    ingredients='Salt\nPepper (1 tsp)\nGarlic')
        error_msg = str(errors)
        self.assertIn('Line 1', error_msg)
        self.assertIn('Line 3', error_msg)
        self.assertIn('Ingredient name (quantity)', error_msg)

    def test_form_with_empty_lines_in_ingredients(self):
        self._assert_form_valid(ingredients='Flour (500g)\n\nSugar (200g)\n\n')

    def test_form_accepts_zero_prep_and_cook_time(self):
        self._assert_form_valid(prep_time_hours=0, prep_time_minutes=0,
                               cook_time_hours=0, cook_time_minutes=0)

    def test_form_accepts_valid_time_values(self):
        self._assert_form_valid(prep_time_hours=2, prep_time_minutes=30,
                               cook_time_hours=1, cook_time_minutes=45)

    def test_form_rejects_negative_time_values(self):
        self._assert_form_invalid('prep_time_hours', prep_time_hours=-1)
        self._assert_form_invalid('prep_time_minutes', prep_time_minutes=-5)
        self._assert_form_invalid('cook_time_hours', cook_time_hours=-2)
        self._assert_form_invalid('cook_time_minutes', cook_time_minutes=-10)

    def test_form_rejects_minutes_over_59(self):
        self._assert_form_invalid('prep_time_minutes', prep_time_minutes=60)
        self._assert_form_invalid('cook_time_minutes', cook_time_minutes=75)

    def test_form_accepts_minutes_at_59(self):
        self._assert_form_valid(prep_time_minutes=59, cook_time_minutes=59)

    def test_form_accepts_large_time_values(self):
        self._assert_form_valid(prep_time_hours=10, cook_time_hours=8)

    def test_form_rejects_string_in_time_fields(self):
        self._assert_form_invalid('prep_time_hours', prep_time_hours='two')
        self._assert_form_invalid('prep_time_minutes', prep_time_minutes='thirty')
        self._assert_form_invalid('cook_time_hours', cook_time_hours='one')
        self._assert_form_invalid('cook_time_minutes', cook_time_minutes='fifteen')

    def test_form_rejects_decimal_in_time_fields(self):
        self._assert_form_invalid('prep_time_hours', prep_time_hours=1.5)

    def test_form_accepts_optional_image(self):
        self._assert_form_valid()

    def test_form_accepts_valid_image(self):
        uploaded_file = create_test_image()
        form = RecipeForm(data=self.form_data, files={'image': uploaded_file})
        self.assertTrue(form.is_valid())

    def test_form_with_special_characters_in_fields(self):
        self._assert_form_valid(
            title="Chef's Special: 'Delicious!' Recipe",
            ingredients="Chef's secret ingredient (1 tsp)"
        )

    def test_form_with_empty_lines_in_steps(self):
        self._assert_form_valid(steps='Mix flour\n\nAdd sugar\n\n')

    def test_form_saves_correctly(self):
        form = RecipeForm(data=self.form_data)
        self.assertTrue(form.is_valid())
        recipe = form.save(commit=False)
        recipe.author = self.user
        recipe.save()
        self.assertEqual(recipe.title, 'Test Recipe')
        self.assertEqual(recipe.author, self.user)
        self.assertEqual(recipe.servings, 4)
        self.assertEqual(recipe.ingredients, 'test ingredient (1 cup)')
        self.assertEqual(recipe.steps, 'test step 1')

    def test_form_rejects_ingredient_with_multiple_parentheses_not_at_end(self):
        errors = self._assert_form_invalid('ingredients', 
            ingredients='Salt (table) and pepper (1 tsp) extra')
        error_msg = str(errors)
        self.assertIn('Line 1', error_msg)
        self.assertIn('parentheses', error_msg.lower())

    def test_form_rejects_ingredient_with_only_opening_parenthesis(self):
        errors = self._assert_form_invalid('ingredients', 
            ingredients='Flour (500g')
        error_msg = str(errors)
        self.assertIn('Line 1', error_msg)

    def test_form_rejects_ingredient_with_only_closing_parenthesis(self):
        errors = self._assert_form_invalid('ingredients', 
            ingredients='Flour 500g)')
        error_msg = str(errors)
        self.assertIn('Line 1', error_msg)

    def test_form_rejects_ingredient_with_generic_format_error(self):
        errors = self._assert_form_invalid('ingredients', 
            ingredients='InvalidFormatHere')
        error_msg = str(errors)
        self.assertIn('Line 1', error_msg)
        self.assertIn('Ingredient name (quantity)', error_msg)