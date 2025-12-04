from django.test import TestCase
from django.urls import reverse
from recipes.models import Recipe
from recipes.tests.utils import get_default_user, create_test_form_data


class RecipeCreateValidationTestCase(TestCase):
    """tests for recipe creation form validation"""
    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json',
    ]

    def setUp(self):
        self.user = get_default_user()
        self.client.login(username='@johndoe', password='Password123')
        self.url = reverse('create_recipe')
        self.form_data = create_test_form_data()

    def test_recipe_creation_fails_with_short_title(self):
        """test that recipe creation fails with title less than 4 characters"""
        self.form_data['title'] = 'abc'
        initial_recipe_count = Recipe.objects.count()
        response = self.client.post(self.url, self.form_data)
        
        self.assertEqual(Recipe.objects.count(), initial_recipe_count)
        self.assertEqual(response.status_code, 200)
        form = response.context.get('form') if getattr(response, 'context', None) else None
        self.assertIsNotNone(form)
        self.assertIn('title', form.errors)
        self.assertTrue(any('at least' in e or 'Ensure this value has at least' in e for e in form.errors['title']))

    def test_recipe_creation_fails_without_title(self):
        """test that recipe creation fails without title"""
        self.form_data.pop('title')
        initial_recipe_count = Recipe.objects.count()
        response = self.client.post(self.url, self.form_data)
        
        self.assertEqual(Recipe.objects.count(), initial_recipe_count)
        self.assertEqual(response.status_code, 200)
        form = response.context.get('form') if getattr(response, 'context', None) else None
        self.assertIsNotNone(form)
        self.assertIn('title', form.errors)
        self.assertTrue(any('This field is required' in e for e in form.errors['title']))
    
    def test_recipe_creation_fails_without_publication_date(self):
        """test that recipe creation fails without publication date"""
        self.form_data.pop('publication_date')
        initial_recipe_count = Recipe.objects.count()
        response = self.client.post(self.url, self.form_data)
        
        self.assertEqual(Recipe.objects.count(), initial_recipe_count)
        self.assertEqual(response.status_code, 200)
        form = response.context.get('form') if getattr(response, 'context', None) else None
        self.assertIsNotNone(form)
        self.assertIn('publication_date', form.errors)
        self.assertTrue(any('This field is required' in e for e in form.errors['publication_date']))
    
    def test_recipe_creation_fails_without_ingredients(self):
        """test that recipe creation fails without ingredients"""
        self.form_data.pop('ingredients')
        initial_recipe_count = Recipe.objects.count()
        response = self.client.post(self.url, self.form_data)
        
        self.assertEqual(Recipe.objects.count(), initial_recipe_count)
        self.assertEqual(response.status_code, 200)
        form = response.context.get('form') if getattr(response, 'context', None) else None
        self.assertIsNotNone(form)
        self.assertIn('ingredients', form.errors)
        self.assertTrue(any('This field is required' in e for e in form.errors['ingredients']))
    
    def test_recipe_creation_fails_without_steps(self):
        """test that recipe creation fails without steps"""
        self.form_data.pop('steps')
        initial_recipe_count = Recipe.objects.count()
        response = self.client.post(self.url, self.form_data)
        
        self.assertEqual(Recipe.objects.count(), initial_recipe_count)
        self.assertEqual(response.status_code, 200)
        form = response.context.get('form') if getattr(response, 'context', None) else None
        self.assertIsNotNone(form)
        self.assertIn('steps', form.errors)
        self.assertTrue(any('This field is required' in e for e in form.errors['steps']))

    def test_recipe_creation_fails_without_servings(self):
        """test that recipe creation fails without servings"""
        self.form_data.pop('servings')
        initial_recipe_count = Recipe.objects.count()
        response = self.client.post(self.url, self.form_data)
        
        self.assertEqual(Recipe.objects.count(), initial_recipe_count)
        self.assertEqual(response.status_code, 200)
        form = response.context.get('form') if getattr(response, 'context', None) else None
        self.assertIsNotNone(form)
        self.assertIn('servings', form.errors)
        self.assertTrue(any('Please enter the number of servings' in e for e in form.errors['servings']))
    
    def test_recipe_creation_fails_with_invalid_date_format(self):
        """test that recipe creation handles invalid date format"""
        self.form_data['publication_date'] = 'invalid-date'
        initial_recipe_count = Recipe.objects.count()
        response = self.client.post(self.url, self.form_data)
        
        self.assertEqual(Recipe.objects.count(), initial_recipe_count)
        self.assertEqual(response.status_code, 200)
        form = response.context.get('form') if getattr(response, 'context', None) else None
        self.assertIsNotNone(form)
        self.assertIn('publication_date', form.errors)
        self.assertTrue(any('Enter a valid date' in e or 'Enter a valid' in e for e in form.errors['publication_date']))
    
    def test_recipe_creation_with_max_length_title(self):
        """test that title can be up to 255 characters"""
        self.form_data['title'] = 'A' * 255
        initial_recipe_count = Recipe.objects.count()
        response = self.client.post(self.url, self.form_data, follow=True)
        response = self.client.post(reverse('create_recipe_tags'), {'create_recipe': 'true'}, follow=True)

        self.assertEqual(Recipe.objects.count(), initial_recipe_count + 1)
        
    def test_recipe_creation_fails_with_too_long_title(self):
        """test that title cannot exceed 255 characters"""
        self.form_data['title'] = 'A' * 256
        initial_recipe_count = Recipe.objects.count()
        response = self.client.post(self.url, self.form_data)
        
        self.assertEqual(Recipe.objects.count(), initial_recipe_count)
        self.assertEqual(response.status_code, 200)
        form = response.context.get('form') if getattr(response, 'context', None) else None
        self.assertIsNotNone(form)
        self.assertIn('title', form.errors)
        self.assertTrue(any('at most 255' in e or 'Ensure this value has at most' in e for e in form.errors['title']))

    def test_recipe_creation_with_special_characters_in_title(self):
        """test create recipe with special characters in title"""
        self.form_data['title'] = 'Test Recipe! @#&*()_+[]{};:,.<>?'
        initial_recipe_count = Recipe.objects.count()
        response = self.client.post(self.url, self.form_data, follow=True)
        response = self.client.post(reverse('create_recipe_tags'), {'create_recipe': 'true'}, follow=True)

        self.assertEqual(Recipe.objects.count(), initial_recipe_count + 1)
        created_recipe = Recipe.objects.latest('id')
        self.assertEqual(created_recipe.title, 'Test Recipe! @#&*()_+[]{};:,.<>?')

    def test_recipe_creation_fails_with_invalid_ingredient_line(self):
        """test that recipe will not be created with invalid ingredients input"""
        self.form_data['ingredients'] = 'Avo (1) avo'
        initial_recipe_count = Recipe.objects.count()
        response = self.client.post(self.url, self.form_data)

        self.assertEqual(Recipe.objects.count(), initial_recipe_count)
        self.assertEqual(response.status_code, 200)
        form = response.context.get('form') if getattr(response, 'context', None) else None
        self.assertIsNotNone(form)
        self.assertIn('ingredients', form.errors)
        self.assertTrue(any('Parentheses should be at the end' in e or 'Please fix the following' in e for e in form.errors['ingredients']))

    def test_recipe_creation_with_valid_time_values(self):
        """test recipe creation with valid time values"""
        self.form_data['prep_time_hours'] = 2
        self.form_data['prep_time_minutes'] = 30
        self.form_data['cook_time_hours'] = 1
        self.form_data['cook_time_minutes'] = 45
        initial_recipe_count = Recipe.objects.count()

        response = self.client.post(self.url, self.form_data, follow=True)
        response = self.client.post(reverse('create_recipe_tags'), {'create_recipe':'true'}, follow=True)

        self.assertEqual(Recipe.objects.count(), initial_recipe_count + 1)
        created_recipe = Recipe.objects.latest('id')
        self.assertEqual(created_recipe.prep_time_hours, 2)
        self.assertEqual(created_recipe.prep_time_minutes, 30)
        self.assertEqual(created_recipe.cook_time_hours, 1)
        self.assertEqual(created_recipe.cook_time_minutes, 45)

    def test_recipe_creation_with_zero_times(self):
        """test recipe creation with zero time values"""
        self.form_data['prep_time_hours'] = 0
        self.form_data['prep_time_minutes'] = 0
        self.form_data['cook_time_hours'] = 0
        self.form_data['cook_time_minutes'] = 0
        initial_recipe_count = Recipe.objects.count()

        response = self.client.post(self.url, self.form_data, follow=True)
        response = self.client.post(reverse('create_recipe_tags'), {'create_recipe':'true'}, follow=True)

        self.assertEqual(Recipe.objects.count(), initial_recipe_count + 1)