from django.test import TestCase
from django.urls import reverse
from recipes.models import Recipe, User
from django.utils import timezone
from datetime import timedelta

class AllRecipesViewTestCase(TestCase):
    """Tests for the all recipes view."""
    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.url = reverse('all_recipes')

        # Log user in 
        self.client.login(username='@johndoe', password='Password123')

        # Create recipes
        self.recipe1 = Recipe.objects.create(
            author=self.user,
            title="Overnight Oats",
            adjectives="cheap healthy easy",
            publication_date=timezone.now().date()
        )

        self.recipe2 = Recipe.objects.create(
            author=self.user,
            title="One Pot Chicken and Rice",
            adjectives = "protein healthy",
            publication_date=timezone.now().date()
        )

    def test_all_recipes_url(self):
        self.assertEqual(self.url, '/all_recipes/')

    def test_get_all_recipes(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'all_recipes.html')

    def test_all_recipes_list_is_in_context(self):
        response = self.client.get(self.url)
        recipes = response.context['recipes']
        self.assertIn(self.recipe1, recipes)
        self.assertIn(self.recipe2, recipes)
    
    def test_login_required(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302) # Redirect to login

    def test_all_recipes_with_exactly_25_recipes(self):
        Recipe.objects.all().delete()
        for i in range(25):
            Recipe.objects.create(
            author=self.user,
            title=f"Recipe {i}",
            adjectives="test",
            publication_date=timezone.now().date()
        )
        response = self.client.get(self.url)
        self.assertEqual(response.context['page_object'].paginator.num_pages, 1)
        self.assertFalse(response.context['page_object'].has_other_pages)

    def test_all_recipes_with_26_recipes(self):
        Recipe.objects.all().delete()
        for i in range(26):
            Recipe.objects.create(
                author=self.user,
                title=f"Recipe {i}",
                adjectives="test",
                publication_date=timezone.now().date()
            )
        response = self.client.get(self.url)
        self.assertEqual(response.context['page_object'].paginator.num_pages, 2)

    def test_all_recipes_ordering(self):
        """Test that recipes are ordered by publication date (newest first)"""
        Recipe.objects.all().delete()
        old_recipe = Recipe.objects.create(
            author=self.user,
            title="Old Recipe",
            adjectives="old",
            publication_date = timezone.now().date() - timedelta(days=10)
        )
        new_recipe = Recipe.objects.create(
            author=self.user,
            title="New Recipe",
            adjectives="new",
            publication_date=timezone.now().date()
        )
        response = self.client.get(self.url)
        recipes = response.context['recipes']
        self.assertEqual(recipes[0], new_recipe)  # Newest first
        self.assertEqual(recipes[1], old_recipe)  # Older second
    
    def test_pagination_works(self):
    # Clear existing recipes first
        Recipe.objects.all().delete()
    
        # Create exactly 55 recipes (3 pages)
        for i in range(55):
            Recipe.objects.create(
                author=self.user,
                title=f"Recipe {i}",
                adjectives="test",
                publication_date=timezone.now().date()
            )
        response = self.client.get(self.url)
        self.assertEqual(response.context['page_object'].paginator.num_pages, 3)
        self.assertEqual(response.context['page_object'].paginator.count, 55)
    
    def test_pagination_first_page(self):
        """Test content of first page"""
        response = self.client.get(self.url)
        self.assertContains(response, self.recipe1.title)
        self.assertContains(response, "Page 1 of")

    def test_invalid_page_number(self):
        """Test handling of invalid page parameter"""
        response = self.client.get(self.url + '?page=999')
        self.assertEqual(response.status_code, 200)  # Should show last page
    
    def test_non_numeric_page_parameter(self):
        """Test handling of non-numeric page parameter"""
        response = self.client.get(self.url + '?page=abc')
        self.assertEqual(response.status_code, 200)  # Should show first page