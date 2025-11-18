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
        self.form_data = {
            'author': self.user.id,
            'title': 'Test Recipe',
            'adjectives': 'quick easy',
            'publication_date': timezone.now().date()
        }

    # Test that form is valid with correct data
    def test_valid_form(self):
        form = RecipeForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    # Test that form has all necessary fields
    def test_form_has_necessary_fields(self):
        form = RecipeForm()
        self.assertIn('author', form.fields)
        self.assertIn('title', form.fields)
        self.assertIn('adjectives', form.fields)
        self.assertIn('publication_date', form.fields)

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
        recipe = form.save()
        self.assertEqual(recipe.title, 'Test Recipe')
        self.assertEqual(recipe.adjectives, 'quick easy')
        self.assertEqual(recipe.author, self.user)

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