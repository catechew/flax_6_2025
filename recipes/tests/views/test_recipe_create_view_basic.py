from django.test import TestCase
from django.urls import reverse
from recipes.models import Recipe
from recipes.tests.utils import get_default_user, create_test_form_data


class RecipeCreateBasicTestCase(TestCase):
    """Tests for basic recipe creation view functionality"""
    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json',
    ]

    def setUp(self):
        self.user = get_default_user()
        self.client.login(username='@johndoe', password='Password123')
        self.url = reverse('create_recipe')
        self.form_data = create_test_form_data()

    def test_create_recipe_url(self):
        """test that the create recipe url is correct"""
        self.assertEqual(self.url, '/create_recipe/')

    def test_get_create_recipe_page(self):
        """test get request to create recipe page"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/recipe_form.html')

    def test_create_recipe_form_in_context(self):
        """test that form is passed to template context"""
        response = self.client.get(self.url)
        self.assertIn('form', response.context)
        from recipes.forms.recipe_form import RecipeForm
        self.assertIsInstance(response.context['form'], RecipeForm)
    
    def test_create_recipe_form_fields(self):
        """test that form has all required fields"""
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
        self.assertIn('private', form.fields)

    def test_successful_recipe_creation(self):
        """test successful recipe creation"""
        initial_recipe_count = Recipe.objects.count()
        response = self.client.post(self.url, self.form_data)
        
        self.assertRedirects(response, reverse('create_recipe_tags'))

    def test_cancel_button_present_in_template(self):
        """test that cancel button is present in the template"""
        response = self.client.get(self.url)
        self.assertContains(response, 'Cancel')
        self.assertContains(response, reverse('all_recipes'))
    
    def test_submit_button_present_in_template(self):
        """test that submit button is present in the template"""
        response = self.client.get(self.url)
        self.assertContains(response, 'Create Recipe')
        self.assertContains(response, 'type="submit"')