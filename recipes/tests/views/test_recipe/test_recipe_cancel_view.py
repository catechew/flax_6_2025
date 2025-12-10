from django.test import TestCase, RequestFactory
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.messages.storage.fallback import FallbackStorage
from django.urls import reverse

from recipes.handlers.recipe_form_handler import RecipeFormHandler
from recipes.models import Recipe, User
from recipes.views.recipe_cancel_view import cancel_recipe_operation
from django.utils import timezone


class RecipeCancelViewTestCase(TestCase):
    """
    Tests for recipe cancel view.
    """

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.recipe = Recipe.objects.create(
            title='Test Recipe',
            author=self.user,
            publication_date=timezone.now().date(),
            servings=4,
            ingredients='Test (1)',
            steps='Test steps',
            prep_time_hours=0,
            prep_time_minutes=30,
            cook_time_hours=1,
            cook_time_minutes=15,
            private=False
        )

    def get_request(self, user=None):
        """ Create a GET request with session and messages. """
        factory = RequestFactory()
        request = factory.get('/test/')
        request.user = user or self.user
        request.session = SessionStore()
        request.session.create()
        setattr(request, '_messages', FallbackStorage(request))
        return request

    def test_cancel_create_redirects_to_all_recipes(self):
        """ Test canceling recipe create redirects to all recipes. """
        request = self.get_request()
        response = cancel_recipe_operation(request, recipe_id=None)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('recipes', response.url)

    def test_cancel_update_redirects_to_recipe_detail(self):
        """ Test canceling recipe update redirects to recipe detail. """
        request = self.get_request()
        response = cancel_recipe_operation(request, recipe_id=self.recipe.id)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('recipe', response.url)
        self.assertIn(str(self.recipe.id), response.url)

    def test_cancel_without_session_data(self):
        """ Test canceling when no session data exists. """
        request = self.get_request()
        response = cancel_recipe_operation(request, recipe_id=None)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('recipes', response.url)

    def test_cancel_with_session_data_cleans_up(self):
        """ Test canceling with session data cleans it up. """
        request = self.get_request()
        handler = RecipeFormHandler(request)
        handler.session_data['form_data'] = {'title': 'Test'}
        request.session.modified = True
        
        response = cancel_recipe_operation(request, recipe_id=None)
        
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(handler.session_key, request.session)