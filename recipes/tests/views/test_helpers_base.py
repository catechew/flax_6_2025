from django.test import TestCase
from recipes.models import User, Recipe
from django.utils import timezone

class BaseRecipeViewTestCase(TestCase):
    """
    Base test case for recipe views with common setup.
    """
    
    fixtures = ['recipes/tests/fixtures/default_user.json']
    
    def setUp(self):
        """ Set up test user and log them in. """
        self.user = User.objects.get(username='@johndoe')
        self.client.login(username='@johndoe', password='Password123')
        
    def create_test_recipe(self, **kwargs):
        """
        Helper to create recipes with sensible defaults.
        Override any field by passing it as a keyword argument.
        """
        defaults = {
            'author': self.user,
            'title': 'Test Recipe',
            'publication_date': timezone.now().date(),
            'ingredients': 'test (1)',
            'steps': 'test',
            'servings': 4
        }
        defaults.update(kwargs)
        return Recipe.objects.create(**defaults)