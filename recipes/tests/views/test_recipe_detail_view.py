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
    
    def test_recipe_detail_with_negative_id(self):
        url = reverse('recipe_detail', kwargs={'recipe_id': -1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_recipe_detail_with_zero_id(self):
        url = reverse('recipe_detail', kwargs={'recipe_id': 0})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_recipe_detail_with_very_large_id(self):
        url = reverse('recipe_detail', kwargs={'recipe_id': 999999999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_recipe_detail_displays_title(self):
        """Test that recipe title is displayed on the page"""
        response = self.client.get(self.url)
        self.assertContains(response, "Korean Noodles")
    
    def test_recipe_detail_displays_adjectives(self):
        """Test that recipe adjectives are displayed on the page"""
        response = self.client.get(self.url)
        self.assertContains(response, "quick easy")
        self.assertContains(response, self.recipe.adjectives)
    
    def test_recipe_detail_displays_author(self):
        """Test that recipe author username is displayed"""
        response = self.client.get(self.url)
        self.assertContains(response, self.user.username)
    
    def test_recipe_detail_with_long_title(self):
        """Test displaying recipe with maximum length title"""
        long_title = "A" * 255
        recipe = Recipe.objects.create(
            author=self.user,
            title=long_title,
            adjectives="test",
            publication_date=timezone.now().date()
        )
        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, long_title)
    
    def test_recipe_detail_with_minimum_length_title(self):
        """Test displaying recipe with minimum valid title (4 chars)"""
        recipe = Recipe.objects.create(
            author=self.user,
            title="ABCD",
            adjectives="test",
            publication_date=timezone.now().date()
        )
        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ABCD")
    
    def test_recipe_detail_with_special_characters(self):
        """Test displaying recipe with special characters in title"""
        recipe = Recipe.objects.create(
            author=self.user,
            title="Grandmother's Secret Recipe! (The Best)",
            adjectives="special",
            publication_date=timezone.now().date()
        )
        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Grandmother&#x27;s Secret Recipe! (The Best)")
    
    def test_recipe_detail_from_different_author(self):
        """Test viewing recipe created by a different user"""
        try:
            other_user = User.objects.get(username='@janedoe')
        except User.DoesNotExist:
            other_user = User.objects.create_user(
                username='@janedoe',
                email='jane@example.com',
                password='Password123'
            )
        other_recipe = Recipe.objects.create(
            author=other_user,
            title="Jane's Recipe",
            adjectives="collaborative",
            publication_date=timezone.now().date()
        )
        url = reverse('recipe_detail', kwargs={'recipe_id': other_recipe.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Jane's Recipe")
        self.assertContains(response, other_user.username)