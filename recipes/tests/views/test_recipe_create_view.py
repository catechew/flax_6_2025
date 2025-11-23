from django.test import TestCase
from django.urls import reverse
from recipes.models import Recipe, User
from django.utils import timezone
from datetime import timedelta
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from io import BytesIO

class RecipeCreateViewTestCase(TestCase):
    """ Tests for the create recipe view """

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.client.login(username='@johndoe', password='Password123')
        self.url = reverse('create_recipe')

        self.form_data = {
            'title' : 'Test Recipe',
            'publication_date' : timezone.now().date(),
            'servings' : 4,
            'ingredients' : "test (1)",
            'steps' : "test",
            'prep_time_hours': 0,
            'prep_time_minutes': 30,
            'cook_time_hours': 1,
            'cook_time_minutes': 15,
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
        self.assertIn('title', form.fields)
        self.assertIn('publication_date', form.fields)
        self.assertIn('ingredients', form.fields)
        self.assertIn('steps', form.fields)
        self.assertIn('prep_time_hours', form.fields)
        self.assertIn('prep_time_minutes', form.fields)
        self.assertIn('cook_time_hours', form.fields)
        self.assertIn('cook_time_minutes', form.fields)

    # Test successful recipe creation
    def test_successful_recipe_creation(self):
        initial_recipe_count = Recipe.objects.count()
        response = self.client.post(self.url, self.form_data, follow=True)

        # Should redirect to page 2 (tags)
        self.assertRedirects(response, reverse('create_recipe_tags'))

        # Page 2: Post with create_recipe button (no tags)
        response = self.client.post(reverse('create_recipe_tags'), {'create_recipe':'true'}, follow=True)

        # Check that recipe was created
        self.assertEqual(Recipe.objects.count(), initial_recipe_count + 1)

        # Check the created recipe
        created_recipe = Recipe.objects.latest('id')
        self.assertEqual(created_recipe.title, 'Test Recipe')
        self.assertEqual(created_recipe.author, self.user)
        self.assertEqual(created_recipe.servings, 4)
        self.assertEqual(created_recipe.ingredients, 'test (1)')
        self.assertEqual(created_recipe.steps, 'test')
        self.assertEqual(created_recipe.prep_time_hours, 0)
        self.assertEqual(created_recipe.prep_time_minutes, 30)
        self.assertEqual(created_recipe.cook_time_hours, 1)
        self.assertEqual(created_recipe.cook_time_minutes, 15)

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
    
    # Test that recipe creation fails without ingredients
    def test_recipe_creation_fails_without_ingredients(self):
        self.form_data.pop('ingredients')  # Remove ingredients from form data
        initial_recipe_count = Recipe.objects.count()
        response = self.client.post(self.url, self.form_data)
        # Check that recipe was not created
        self.assertEqual(Recipe.objects.count(), initial_recipe_count)
        self.assertEqual(response.status_code, 200)
        form = response.context.get('form') if getattr(response, 'context', None) else None
        self.assertIsNotNone(form)
        self.assertIn('ingredients', form.errors)
        self.assertTrue(any('This field is required' in e for e in form.errors['ingredients']))
    
    # Test that recipe creation fails without steps
    def test_recipe_creation_fails_without_steps(self):
        self.form_data.pop('steps')  # Remove ingredients from form data
        initial_recipe_count = Recipe.objects.count()
        response = self.client.post(self.url, self.form_data)
        # Check that recipe was not created
        self.assertEqual(Recipe.objects.count(), initial_recipe_count)
        self.assertEqual(response.status_code, 200)
        form = response.context.get('form') if getattr(response, 'context', None) else None
        self.assertIsNotNone(form)
        self.assertIn('steps', form.errors)
        self.assertTrue(any('This field is required' in e for e in form.errors['steps']))

    # Test that recipe creation fails without servings
    def test_recipe_creation_fails_without_servings(self):
        self.form_data.pop('servings')  # Remove ingredients from form data
        initial_recipe_count = Recipe.objects.count()
        response = self.client.post(self.url, self.form_data)
        # Check that recipe was not created
        self.assertEqual(Recipe.objects.count(), initial_recipe_count)
        self.assertEqual(response.status_code, 200)
        form = response.context.get('form') if getattr(response, 'context', None) else None
        self.assertIsNotNone(form)
        self.assertIn('servings', form.errors)
        self.assertTrue(any('Please enter the number of servings' in e for e in form.errors['servings']))
    
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
        response = self.client.post(reverse('create_recipe_tags'), {'create_recipe': 'true'}, follow=True)

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

    # Test create recipe with special characters in title
    def test_recipe_creation_with_special_characters_in_title(self):
        self.form_data['title'] = 'Test Recipe! @#&*()_+[]{};:,.<>?'
        initial_recipe_count = Recipe.objects.count()
        response = self.client.post(self.url, self.form_data, follow=True)
        response = self.client.post(reverse('create_recipe_tags'), {'create_recipe': 'true'}, follow=True)


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
            response = self.client.post(reverse('create_recipe_tags'), {'create_recipe': 'true'}, follow=True)
            self.assertEqual(response.status_code, 200)
        
        self.assertEqual(Recipe.objects.count(), initial_recipe_count + 5)

    # Test that creating a recipe with future publication date fails
    def test_create_recipe_with_future_date_fails(self):
        future_date = timezone.now().date() + timedelta(days=1)
        self.form_data['publication_date'] = future_date
        initial_recipe_count = Recipe.objects.count()

        response = self.client.post(self.url, self.form_data)

        # Recipe should not be created
        self.assertEqual(Recipe.objects.count(), initial_recipe_count)
        self.assertEqual(response.status_code, 200)
        # Inspect form errors directly (assertFormError may not work with TemplateResponse)
        form = response.context.get('form') if getattr(response, 'context', None) else None
        self.assertIsNotNone(form)
        self.assertIn('publication_date', form.errors)
        self.assertTrue(any('Publication date cannot be in the future' in e for e in form.errors['publication_date']))

    # Test that tomorrow's date is rejected
    def test_create_recipe_with_tomorrow_fails(self):
        tomorrow = timezone.now().date() + timedelta(days=1)
        self.form_data['publication_date'] = tomorrow
        initial_recipe_count = Recipe.objects.count()

        response = self.client.post(self.url, self.form_data)

        self.assertEqual(Recipe.objects.count(), initial_recipe_count)
        form = response.context.get('form') if getattr(response, 'context', None) else None
        self.assertIsNotNone(form)
        self.assertIn('publication_date', form.errors)
        self.assertTrue(any('Publication date cannot be in the future' in e for e in form.errors['publication_date']))

    # Test that dates far in the future are rejected
    def test_create_recipe_with_far_future_date_fails(self):
        far_future = timezone.now().date() + timedelta(days=365)
        self.form_data['publication_date'] = far_future
        initial_recipe_count = Recipe.objects.count()

        response = self.client.post(self.url, self.form_data)

        self.assertEqual(Recipe.objects.count(), initial_recipe_count)
        self.assertEqual(response.status_code, 200)

    # Test that today's date is accepted
    def test_create_recipe_with_today_succeeds(self):
        self.form_data['publication_date'] = timezone.now().date()
        initial_recipe_count = Recipe.objects.count()

        response = self.client.post(self.url, self.form_data, follow=True)
        response = self.client.post(reverse('create_recipe_tags'), {'create_recipe': 'true'}, follow=True)


        self.assertEqual(Recipe.objects.count(), initial_recipe_count + 1)
        new_recipe = Recipe.objects.latest('id')
        self.assertEqual(new_recipe.publication_date, timezone.now().date())

    # Test that yesterday's date is accepted
    def test_create_recipe_with_yesterday_succeeds(self):
        yesterday = timezone.now().date() - timedelta(days=1)
        self.form_data['publication_date'] = yesterday
        initial_recipe_count = Recipe.objects.count()

        response = self.client.post(self.url, self.form_data, follow=True)
        response = self.client.post(reverse('create_recipe_tags'), {'create_recipe': 'true'}, follow=True)

        self.assertEqual(Recipe.objects.count(), initial_recipe_count + 1)
        new_recipe = Recipe.objects.latest('id')
        self.assertEqual(new_recipe.publication_date, yesterday)

    # Test that past dates are accepted
    def test_create_recipe_with_past_date_succeeds(self):
        past_date = timezone.now().date() - timedelta(days=30)
        self.form_data['publication_date'] = past_date
        initial_recipe_count = Recipe.objects.count()

        response = self.client.post(self.url, self.form_data, follow=True)
        response = self.client.post(reverse('create_recipe_tags'), {'create_recipe': 'true'}, follow=True)

        self.assertEqual(Recipe.objects.count(), initial_recipe_count + 1)
        new_recipe = Recipe.objects.latest('id')
        self.assertEqual(new_recipe.publication_date, past_date)

    # Test that date widget has max attribute set to today
    def test_create_recipe_date_widget_has_max_attribute(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        # Check that the form contains a date input with max attribute
        form_html = str(response.content)
        self.assertIn('type="date"', form_html)
        self.assertIn('max=', form_html)

    # Test that adding an image succeeds
    def test_create_recipe_with_image_upload_succeeds(self):
        initial_recipe_count = Recipe.objects.count()

        # Create a real valid image file
        image = Image.new('RGB', (100, 100), color='red')
        image_file = BytesIO()
        image.save(image_file, 'JPEG')
        image_file.seek(0)

        uploaded_file = SimpleUploadedFile(
            name='test.jpg',
            content=image_file.read(),
            content_type='image/jpeg'
        )

        data = self.form_data.copy()
        data['image'] = uploaded_file

        response = self.client.post(self.url, data, format='multipart', follow=True)
        response = self.client.post(reverse('create_recipe_tags'), {'create_recipe': 'true'}, follow=True)

        self.assertEqual(response.status_code, 200)
        # Recipe should be created
        self.assertEqual(Recipe.objects.count(), initial_recipe_count + 1)
        created_recipe = Recipe.objects.latest('id')
        # Image field should be populated
        self.assertTrue(bool(created_recipe.image))

    # Test that recipe will not be created with invalid ingredients input
    # e.g. "Avo (1) avo" --> should end with ')'
    def test_recipe_creation_fails_with_invalid_ingredient_line(self):
        self.form_data['ingredients'] = 'Avo (1) avo'  # invalid: text after closing parenthesis
        initial_recipe_count = Recipe.objects.count()
        response = self.client.post(self.url, self.form_data)

        # Recipe should not be created
        self.assertEqual(Recipe.objects.count(), initial_recipe_count)
        self.assertEqual(response.status_code, 200)
        form = response.context.get('form') if getattr(response, 'context', None) else None
        self.assertIsNotNone(form)
        self.assertIn('ingredients', form.errors)
        # The validation error should mention parentheses position or the generic fix message
        self.assertTrue(any('Parentheses should be at the end' in e or 'Please fix the following' in e for e in form.errors['ingredients']))

    # Test recipe creation with valid time values
    def test_recipe_creation_with_valid_time_values(self):
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

    # Test recipe creation with zero time values
    def test_recipe_creation_with_zero_times(self):
        self.form_data['prep_time_hours'] = 0
        self.form_data['prep_time_minutes'] = 0
        self.form_data['cook_time_hours'] = 0
        self.form_data['cook_time_minutes'] = 0
        initial_recipe_count = Recipe.objects.count()

        response = self.client.post(self.url, self.form_data, follow=True)
        response = self.client.post(reverse('create_recipe_tags'), {'create_recipe':'true'}, follow=True)

        self.assertEqual(Recipe.objects.count(), initial_recipe_count + 1)

    # Test that page 2 url exists
    def test_create_recipe_tags_url(self):
        self.assertEqual(reverse('create_recipe_tags'), '/create_recipe/tags/')


                                    

