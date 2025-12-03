from django.test import TestCase, RequestFactory
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.messages.storage.fallback import FallbackStorage
from recipes.handlers.recipe_form_handler import RecipeFormHandler
from recipes.models import Recipe, User
from django.utils import timezone


class RecipeFormHandlerTestCase(TestCase):

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json',
    ]

    def setUp(self):
        """Set up test fixtures"""
        self.user = User.objects.get(username='@johndoe')
        self.other_user = User.objects.get(username='@janedoe')
        
        # Create a test recipe
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

    def _get_request(self, user=None):
        """Create a GET request with session and messages"""
        factory = RequestFactory()
        request = factory.get('/test/')
        request.user = user or self.user
        
        # Add proper session
        request.session = SessionStore()
        request.session.create()
        
        # Add messages support
        setattr(request, '_messages', FallbackStorage(request))
        
        return request

    # Test create mode
    def test_create_mode(self):
        """Test handler in create mode"""
        request = self._get_request()
        handler = RecipeFormHandler(request, recipe_id=None)
        
        self.assertTrue(handler.is_create_mode)
        self.assertFalse(handler.is_update_mode)
        self.assertIsNone(handler.recipe)
        self.assertTrue(handler.is_owner)

    # Test update mode as owner
    def test_update_mode_owner(self):
        """Test handler in update mode as owner"""
        request = self._get_request(user=self.user)
        handler = RecipeFormHandler(request, recipe_id=self.recipe.id)
        
        self.assertFalse(handler.is_create_mode)
        self.assertTrue(handler.is_update_mode)
        self.assertEqual(handler.recipe, self.recipe)
        self.assertTrue(handler.is_owner)

    # Test update mode as non-owner
    def test_update_mode_non_owner(self):
        """Test handler in update mode as non-owner"""
        request = self._get_request(user=self.other_user)
        handler = RecipeFormHandler(request, recipe_id=self.recipe.id)
        
        self.assertFalse(handler.is_owner)

    # Test base context
    def test_get_base_context(self):
        """Test base context has required fields"""
        request = self._get_request()
        handler = RecipeFormHandler(request)
        context = handler.get_base_context()
        
        self.assertIn('mode', context)
        self.assertIn('is_owner', context)

    # Test tags context
    def test_get_tags_context(self):
        """Test tags context has tag fields"""
        request = self._get_request()
        handler = RecipeFormHandler(request)
        context = handler.get_tags_context()
        
        self.assertIn('course_tags', context)
        self.assertIn('dietary_tags', context)
        self.assertIn('has_image', context)

    # Test redirects work
    def test_redirect_methods(self):
        """Test all redirect methods return redirects"""
        request = self._get_request()
        handler = RecipeFormHandler(request)
        
        # Test each redirect returns a redirect response (status 302)
        self.assertEqual(handler.redirect_to_form_page().status_code, 302)
        self.assertEqual(handler.redirect_to_tags_page().status_code, 302)
        self.assertEqual(handler.redirect_to_detail_page(1).status_code, 302)
        self.assertEqual(handler.redirect_to_cancel_destination().status_code, 302)

    # Test session is marked modified
    def test_mark_session_modified(self):
        """Test session modified flag is set"""
        request = self._get_request()
        handler = RecipeFormHandler(request)
        
        handler.mark_session_modified()
        
        self.assertTrue(request.session.modified)