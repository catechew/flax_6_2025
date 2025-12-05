from django.test import TestCase, RequestFactory
from django.contrib.sessions.backends.db import SessionStore
from django.utils import timezone

from recipes.views.recipe_cancel_view import cancel_recipe_operation
from recipes.models import Recipe, User


class CancelRecipeOperationTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='@testuser',
            email='test@example.com',
            password='Password123',
        )
        self.recipe = Recipe.objects.create(
            author=self.user,
            title='Cancel Test Recipe',
            publication_date=timezone.now().date(),
            ingredients='Test (1)',
            steps='Test steps',
            servings=2,
        )

    def _add_session(self, request):
        request.session = SessionStore()
        request.session.create()
        return request

    def test_cancel_with_session_key_triggers_cleanup(self):
        request = self.factory.get('/cancel/')
        request.user = self.user
        self._add_session(request)
        
        from recipes.helpers.recipe_form_helpers import get_session_key
        key = get_session_key(self.recipe.id)
        
        request.session[key] = {'dummy': 'data'}
        response = cancel_recipe_operation(request, recipe_id=self.recipe.id)
        self.assertEqual(response.status_code, 302)

    def test_cancel_no_session_key(self):
        request = self.factory.get('/cancel/')
        request.user = self.user
        
        self._add_session(request)
        response = cancel_recipe_operation(request, recipe_id=self.recipe.id)
        self.assertEqual(response.status_code, 302)
