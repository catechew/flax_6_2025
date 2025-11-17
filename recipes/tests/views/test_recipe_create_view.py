from django.test import TestCase
from django.urls import reverse
from recipes.models import Recipe, User
from django.utils import timezone

class RecipeCreateViewTestCase(TestCase):
    """ Tests for the create recipe view """

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.url = reverse('create_recipe')

        self.form_data = {
            'author' : self.user.id,
            'title' : 'Test Recipe',
            'adjectives' : 'quick easy healthy',
            'publication_date' : timezone.now().date(),
        }
    
    # Test that the create recipe url is correct
    def test_create_recipe_url(self):
        self.assertEqual(self.url, '/create_recipe/')

    # Test GET request to create recipe page
    def test_get_create_recipe_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_recipe.html')

    # Test that form is passed to template context
    def test_create_recipe_form_in_context(self):
        response = self.client.get(self.url)
        self.assertIn('form', response.context)
        from recipes.forms.recipe_form import RecipeForm
        self.assertIsInstance(response.context['form'], RecipeForm)
    
    # Test that form has all required fields
    def test_create_recipe_form_fields(self):
        response = self.client.get(self.url)
        form = response.context['form']
        self.assertIn('author', form.fields)
        self.assertIn('title', form.fields)
        self.assertIn('adjectives', form.fields)
        self.assertIn('publication_date', form.fields)

    # Test successful recipe creation
    def test_successful_recipe_creation(self):
        initial_recipe_count = Recipe.objects.count()
        response = self.client.post(self.url, self.form_data, follow=True)
        # Check that recipe was created
        self.assertEqual(Recipe.objects.count(), initial_recipe_count + 1)

        # Check the created recipe
        created_recipe = Recipe.objects.latest('id')
        self.assertEqual(created_recipe.title, 'Test Recipe')
        self.assertEqual(created_recipe.adjectives, 'quick easy healthy')
        self.assertEqual(created_recipe.author, self.user)

    # Test that recipe creation fails with title less than 4 characters
    def test_recipe_creation_fails_with_short_title(self):
        self.form_data['title'] = 'abc'  # Title with less than 4 characters
        initial_recipe_count = Recipe.objects.count()
        response = self.client.post(self.url, self.form_data)
        # Check that recipe was not created
        self.assertEqual(Recipe.objects.count(), initial_recipe_count)
        self.assertEqual(response.status_code, 200)
        # The form should have errors for the title field
        form = response.context.get('form') if getattr(response, 'context', None) else None
        self.assertIsNotNone(form)
        self.assertIn('title', form.errors)
        # Validator message may vary; check it mentions the minimum length
        self.assertTrue(any('at least' in e or 'Ensure this value has at least' in e for e in form.errors['title']))
    
    # Test that recipe creation fails with adjectives less than 4 characters
    def test_recipe_creation_fails_with_short_adjectives(self):
        self.form_data['adjectives'] = 'abc'  # Adjectives with less than 4 characters
        initial_recipe_count = Recipe.objects.count()
        response = self.client.post(self.url, self.form_data)
        # Check that recipe was not created
        self.assertEqual(Recipe.objects.count(), initial_recipe_count)
        self.assertEqual(response.status_code, 200)
        form = response.context.get('form') if getattr(response, 'context', None) else None
        self.assertIsNotNone(form)
        self.assertIn('adjectives', form.errors)
        self.assertTrue(any('at least' in e or 'Ensure this value has at least' in e for e in form.errors['adjectives']))

    # Test that recipe creation fails without title
    def test_recipe_creation_fails_without_title(self):
        self.form_data.pop('title')  # Remove title from form data
        initial_recipe_count = Recipe.objects.count()
        response = self.client.post(self.url, self.form_data)
        # Check that recipe was not created
        self.assertEqual(Recipe.objects.count(), initial_recipe_count)
        self.assertEqual(response.status_code, 200)
        form = response.context.get('form') if getattr(response, 'context', None) else None
        self.assertIsNotNone(form)
        self.assertIn('title', form.errors)
        self.assertTrue(any('This field is required' in e for e in form.errors['title']))

    # Test that recipe creation fails without adjectives
    def test_recipe_creation_fails_without_adjectives(self):
        self.form_data.pop('adjectives')  # Remove adjectives from form data
        initial_recipe_count = Recipe.objects.count()
        response = self.client.post(self.url, self.form_data)
        # Check that recipe was not created
        self.assertEqual(Recipe.objects.count(), initial_recipe_count)
        self.assertEqual(response.status_code, 200)
        form = response.context.get('form') if getattr(response, 'context', None) else None
        self.assertIsNotNone(form)
        self.assertIn('adjectives', form.errors)
        self.assertTrue(any('This field is required' in e for e in form.errors['adjectives']))
    
    # Test that recipe creation fails without publication date
    def test_recipe_creation_fails_without_publication_date(self):
        self.form_data.pop('publication_date')  # Remove publication date from form data
        initial_recipe_count = Recipe.objects.count()
        response = self.client.post(self.url, self.form_data)
        # Check that recipe was not created
        self.assertEqual(Recipe.objects.count(), initial_recipe_count)
        self.assertEqual(response.status_code, 200)
        form = response.context.get('form') if getattr(response, 'context', None) else None
        self.assertIsNotNone(form)
        self.assertIn('publication_date', form.errors)
        self.assertTrue(any('This field is required' in e for e in form.errors['publication_date']))
    
    # Test that recipe creation fails without author
    def test_recipe_creation_fails_without_author(self):
        self.form_data.pop('author')  # Remove author from form data
        initial_recipe_count = Recipe.objects.count()
        response = self.client.post(self.url, self.form_data)
        # Check that recipe was not created
        self.assertEqual(Recipe.objects.count(), initial_recipe_count)
        self.assertEqual(response.status_code, 200)
        form = response.context.get('form') if getattr(response, 'context', None) else None
        self.assertIsNotNone(form)
        self.assertIn('author', form.errors)
        self.assertTrue(any('This field is required' in e for e in form.errors['author']))
    
    # Test that recipe creation handles invalid date format
    def test_recipe_creation_fails_with_invalid_date_format(self):
        self.form_data['publication_date'] = 'invalid-date'  # Invalid date format
        initial_recipe_count = Recipe.objects.count()
        response = self.client.post(self.url, self.form_data)
        # Check that recipe was not created
        self.assertEqual(Recipe.objects.count(), initial_recipe_count)
        self.assertEqual(response.status_code, 200)
        form = response.context.get('form') if getattr(response, 'context', None) else None
        self.assertIsNotNone(form)
        self.assertIn('publication_date', form.errors)
        self.assertTrue(any('Enter a valid date' in e or 'Enter a valid' in e for e in form.errors['publication_date']))
    
    # Test that title can be up to 255 characters
    def test_recipe_creation_with_max_length_title(self):
        self.form_data['title'] = 'A' * 255  # Title with 255 characters
        initial_recipe_count = Recipe.objects.count()
        response = self.client.post(self.url, self.form_data, follow=True)

        self.assertEqual(Recipe.objects.count(), initial_recipe_count + 1)
        
    # Test that title cannot exceed 255 characters
    def test_recipe_creation_fails_with_too_long_title(self):
        self.form_data['title'] = 'A' * 256  # Title with 256 characters
        initial_recipe_count = Recipe.objects.count()
        response = self.client.post(self.url, self.form_data)
        
        self.assertEqual(Recipe.objects.count(), initial_recipe_count)
        self.assertEqual(response.status_code, 200)
        form = response.context.get('form') if getattr(response, 'context', None) else None
        self.assertIsNotNone(form)
        self.assertIn('title', form.errors)
        self.assertTrue(any('at most 255' in e or 'Ensure this value has at most' in e for e in form.errors['title']))

    # Test that adjectives can be up to 255 characters
    def test_recipe_creation_with_max_length_adjectives(self):
        self.form_data['adjectives'] = 'test' * 50  # Adjectives with 255 characters
        initial_recipe_count = Recipe.objects.count()
        response = self.client.post(self.url, self.form_data, follow=True)

        self.assertEqual(Recipe.objects.count(), initial_recipe_count + 1)
    
    # Test that adjectives cannot exceed 255 characters
    def test_recipe_creation_fails_with_too_long_adjectives(self):
        # Ensure we exceed 255 characters for the adjectives field
        self.form_data['adjectives'] = 'a' * 256
        initial_recipe_count = Recipe.objects.count()
        response = self.client.post(self.url, self.form_data)

        self.assertEqual(Recipe.objects.count(), initial_recipe_count)
        self.assertEqual(response.status_code, 200)
        form = response.context.get('form') if getattr(response, 'context', None) else None
        self.assertIsNotNone(form)
        self.assertIn('adjectives', form.errors)
        self.assertTrue(any('at most 255' in e or 'Ensure this value has at most' in e for e in form.errors['adjectives']))

    # Test create recipe with special characters in title
    def test_recipe_creation_with_special_characters_in_title(self):
        self.form_data['title'] = 'Test Recipe! @#&*()_+[]{};:,.<>?'
        initial_recipe_count = Recipe.objects.count()
        response = self.client.post(self.url, self.form_data, follow=True)

        self.assertEqual(Recipe.objects.count(), initial_recipe_count + 1)
        created_recipe = Recipe.objects.latest('id')
        self.assertEqual(created_recipe.title, 'Test Recipe! @#&*()_+[]{};:,.<>?')

    # Test that cancel button is present in the template
    def test_cancel_button_present_in_template(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'Cancel')
        self.assertContains(response, reverse('all_recipes'))
    
    # Test that submit button is present in the template
    def test_submit_button_present_in_template(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'Create Recipe')
        self.assertContains(response, 'type="submit"')
    
    # Test creating multiple recipes one after another
    def test_creating_multiple_recipes(self):
        initial_recipe_count = Recipe.objects.count()
        for i in range(5):
            self.form_data['title'] = f'Test Recipe {i}'
            response = self.client.post(self.url, self.form_data, follow=True)
            self.assertEqual(response.status_code, 200)
        
        self.assertEqual(Recipe.objects.count(), initial_recipe_count + 5)

    # Test that help/tips section is present in the form
    def test_help_section_present_in_form(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'Tips')

    