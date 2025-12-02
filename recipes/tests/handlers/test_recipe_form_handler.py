from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import AnonymousUser
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

    def get_request(self, user=None):
        """Create a simple GET request with session"""
        factory = RequestFactory()
        request = factory.get('/test/')
        request.user = user or self.user
        request.session = {}
        return request

    # Test create mode
    def test_create_mode(self):
        """Test handler in create mode"""
        request = self.get_request()
        handler = RecipeFormHandler(request, recipe_id=None)
        
        self.assertTrue(handler.is_create_mode)
        self.assertFalse(handler.is_update_mode)
        self.assertIsNone(handler.recipe)
        self.assertTrue(handler.is_owner)

    # Test update mode as owner
    def test_update_mode_owner(self):
        """Test handler in update mode as owner"""
        request = self.get_request(user=self.user)
        handler = RecipeFormHandler(request, recipe_id=self.recipe.id)
        
        self.assertFalse(handler.is_create_mode)
        self.assertTrue(handler.is_update_mode)
        self.assertEqual(handler.recipe, self.recipe)
        self.assertTrue(handler.is_owner)