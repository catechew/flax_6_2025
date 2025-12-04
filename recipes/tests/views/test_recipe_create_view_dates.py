from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from recipes.models import Recipe
from recipes.tests.utils import get_default_user, create_test_form_data


class RecipeCreateDatesTestCase(TestCase):
    """tests for recipe creation date validation"""
    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json',
    ]

    def setUp(self):
        self.user = get_default_user()
        self.client.login(username='@johndoe', password='Password123')
        self.url = reverse('create_recipe')
        self.form_data = create_test_form_data()

    def test_create_recipe_with_future_date_fails(self):
        """test that creating a recipe with future publication date fails"""
        future_date = timezone.now().date() + timedelta(days=1)
        self.form_data['publication_date'] = future_date
        initial_recipe_count = Recipe.objects.count()

        response = self.client.post(self.url, self.form_data)

        self.assertEqual(Recipe.objects.count(), initial_recipe_count)
        self.assertEqual(response.status_code, 200)
        form = response.context.get('form') if getattr(response, 'context', None) else None
        self.assertIsNotNone(form)
        self.assertIn('publication_date', form.errors)
        # check that the error message has any indication that future date is not allowed
        self.assertTrue(any('Publication date cannot be in the future' in e for e in form.errors['publication_date']))

    def test_create_recipe_with_tomorrow_fails(self):
        """test that tomorrow's date is rejected"""
        tomorrow = timezone.now().date() + timedelta(days=1)
        self.form_data['publication_date'] = tomorrow
        initial_recipe_count = Recipe.objects.count()

        response = self.client.post(self.url, self.form_data)

        self.assertEqual(Recipe.objects.count(), initial_recipe_count)
        form = response.context.get('form') if getattr(response, 'context', None) else None
        self.assertIsNotNone(form)
        self.assertIn('publication_date', form.errors)
        self.assertTrue(any('Publication date cannot be in the future' in e for e in form.errors['publication_date']))

    def test_create_recipe_with_far_future_date_fails(self):
        """test that dates far in the future are rejected"""
        far_future = timezone.now().date() + timedelta(days=365)
        self.form_data['publication_date'] = far_future
        initial_recipe_count = Recipe.objects.count()

        response = self.client.post(self.url, self.form_data)

        self.assertEqual(Recipe.objects.count(), initial_recipe_count)
        self.assertEqual(response.status_code, 200)

    def test_create_recipe_with_today_succeeds(self):
        """test that today's date is accepted"""
        self.form_data['publication_date'] = timezone.now().date()
        initial_recipe_count = Recipe.objects.count()

        response = self.client.post(self.url, self.form_data, follow=True)
        response = self.client.post(reverse('create_recipe_tags'), {'create_recipe': 'true'}, follow=True)

        self.assertEqual(Recipe.objects.count(), initial_recipe_count + 1)
        new_recipe = Recipe.objects.latest('id')
        self.assertEqual(new_recipe.publication_date, timezone.now().date())

    def test_create_recipe_with_yesterday_succeeds(self):
        """test that yesterday's date is accepted"""
        yesterday = timezone.now().date() - timedelta(days=1)
        self.form_data['publication_date'] = yesterday
        initial_recipe_count = Recipe.objects.count()

        response = self.client.post(self.url, self.form_data, follow=True)
        response = self.client.post(reverse('create_recipe_tags'), {'create_recipe': 'true'}, follow=True)

        self.assertEqual(Recipe.objects.count(), initial_recipe_count + 1)
        new_recipe = Recipe.objects.latest('id')
        self.assertEqual(new_recipe.publication_date, yesterday)

    def test_create_recipe_with_past_date_succeeds(self):
        """test that past dates are accepted"""
        past_date = timezone.now().date() - timedelta(days=30)
        self.form_data['publication_date'] = past_date
        initial_recipe_count = Recipe.objects.count()

        response = self.client.post(self.url, self.form_data, follow=True)
        response = self.client.post(reverse('create_recipe_tags'), {'create_recipe': 'true'}, follow=True)

        self.assertEqual(Recipe.objects.count(), initial_recipe_count + 1)
        new_recipe = Recipe.objects.latest('id')
        self.assertEqual(new_recipe.publication_date, past_date)

    def test_create_recipe_date_widget_has_max_attribute(self):
        """test that date widget has max attribute set to today"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        form_html = str(response.content)
        self.assertIn('type="date"', form_html)
        self.assertIn('max=', form_html)