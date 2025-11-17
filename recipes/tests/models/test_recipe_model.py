from django.test import TestCase
from django.utils import timezone
from recipes.models import Recipe, User

class RecipeModelTestCase(TestCase):
    """Tests for the Recipe model, including the __str__ method."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='@testuser',
            first_name='Test',
            last_name='User',
            email='test@example.com',
            password='Password123'
        )

        self.recipe = Recipe.objects.create(
            author=self.user,
            title="Korean Noodles",
            adjectives="quick easy",
            publication_date=timezone.now().date()
        )

    def test_str_method(self):
        expected = (
            f"@testuser "
            f"({self.recipe.publication_date.year}) "
            f"\"Korean Noodles\" Adjectives: quick easy."
        )
        self.assertEqual(str(self.recipe), expected)
