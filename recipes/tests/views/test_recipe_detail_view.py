from django.test import TestCase
from django.urls import reverse
from recipes.models import Recipe, User
from django.utils import timezone 

class RecipeDetailViewTestCase(TestCase):
    """Tests for the recipe detail view."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.client.login(username='@johndoe', password='Password123')

        self.recipe = Recipe.objects.create(
            author=self.user,
            title="Korean Noodles",
            adjectives="quick easy",
            publication_date=timezone.now().date()
        )

        self.url = reverse('recipe_detail', kwargs={'recipe_id': self.recipe.id})

    def test_recipe_detail_url(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
    
    def test_recipe_detail_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'recipe.html')

    def test_recipe_detail_context(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context['recipe'], self.recipe)

    def test_invalid_recipe_id_returns_404(self):
        url = reverse('recipe_detail', kwargs={'recipe_id': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)