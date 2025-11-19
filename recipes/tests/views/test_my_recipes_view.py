"""
Tests for the My Recipes view.
"""
from django.test import TestCase
from django.urls import reverse
from recipes.models import User, Recipe
from datetime import date


class MyRecipesViewTestCase(TestCase):

    """Tests for the my_recipes view."""
    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        """Set up test data before each test."""
        self.url = reverse('my_recipes')
        self.user = User.objects.get(username='@johndoe')
        self.recipe1 = Recipe.objects.create(
            author=self.user,
            title='Test Recipe One',
            adjectives='quick, easy, tasty',
            publication_date=date(2025, 11, 17)
        )
        self.recipe2 = Recipe.objects.create(
            author=self.user,
            title='Test Recipe Two',
            adjectives='healthy, vegetarian',
            publication_date=date(2025, 11, 16)
        )
        self.other_user = User.objects.create_user(
            username='@janedoe',
            email='jane@example.org',
            password='Password123',
            first_name='Jane',
            last_name='Doe'
        )
        self.other_recipe = Recipe.objects.create(
            author=self.other_user,
            title='Other User Recipe',
            adjectives='delicious',
            publication_date=date(2025, 11, 15)
        )

    def test_my_recipes_url(self):
        """Test that the my_recipes URL is correct."""
        self.assertEqual(self.url, '/my_recipes/')

    def test_get_my_recipes_redirects_when_not_logged_in(self):
        """Test that accessing my_recipes redirects to login when not authenticated."""
        response = self.client.get(self.url)
        redirect_url = reverse('log_in') + f'?next={self.url}'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_my_recipes_when_logged_in(self):
        """Test that logged-in users can access their recipes page."""
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_my_recipes_uses_correct_template(self):
        """Test that the correct template is used."""
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'my_recipes.html')

    def test_my_recipes_shows_only_user_recipes(self):
        """Test that users only see their own recipes, not others'."""
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response, 'Test Recipe One')
        self.assertContains(response, 'Test Recipe Two')
        self.assertContains(response, 'quick, easy, tasty')
        self.assertNotContains(response, 'Other User Recipe')

    def test_my_recipes_shows_correct_recipe_count(self):
        """Test that the recipe count is accurate."""
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.context['recipe_count'], 2)

    def test_my_recipes_shows_user_information(self):
        """Test that user's name and username are displayed."""
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response, '@johndoe')
        self.assertContains(response, self.user.first_name)
        self.assertContains(response, self.user.last_name)

    def test_my_recipes_with_no_recipes(self):
        """Test empty page view when user has no recipes."""
        Recipe.objects.filter(author=self.user).delete()
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['recipe_count'], 0)
        self.assertContains(response, "You haven't created any recipes yet")

    def test_my_recipes_displays_recipe_details(self):
        """Test that recipe details are displayed correctly."""
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response, 'Test Recipe One')
        self.assertContains(response, 'quick, easy, tasty')
        self.assertContains(response, 'Nov 17, 2025')

    def test_my_recipes_has_links_to_recipe_actions(self):
        """Test that view/edit/delete links are present."""
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response, 'View')
        self.assertContains(response, 'Edit')
        self.assertContains(response, 'Delete')

    def test_my_recipes_shows_create_recipe_link_when_empty(self):
        """Test that create recipe link appears when no recipes exist."""
        Recipe.objects.filter(author=self.user).delete()
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        create_url = reverse('create_recipe')
        self.assertContains(response, create_url)
        self.assertContains(response, 'Create Your First Recipe')

    def test_my_recipes_context_contains_required_data(self):
        """Test that the context user has all required variables."""
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertIn('user', response.context)
        self.assertIn('recipes', response.context)
        self.assertIn('recipe_count', response.context)
        self.assertEqual(response.context['user'], self.user)

    def test_my_recipes_with_many_recipes(self):
        """Test that page handles many recipes correctly."""
        for i in range(10):
            Recipe.objects.create(
                author=self.user,
                title=f'Recipe Number {i}',
                adjectives='test',
                publication_date=date(2025, 11, 10)
            )
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.context['recipe_count'], 12)
        self.assertEqual(len(response.context['recipes']), 12)

    def test_my_recipes_recipe_ordering(self):
        """Test that recipes are ordered by publication date (newest first)."""
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        recipes = list(response.context['recipes'])
        self.assertEqual(recipes[0].title, 'Test Recipe One') #has publication date as 17th
        self.assertEqual(recipes[1].title, 'Test Recipe Two') #has publication date as 16th

    def test_my_recipes_displays_gravatar(self):
        """Test that user's Gravatar is displayed."""
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response, 'gravatar')

    def test_my_recipes_pluralization(self):
        """Test that recipe/recipes text is pluralized correctly."""
        Recipe.objects.filter(author=self.user).delete()
        Recipe.objects.create(
            author=self.user,
            title='Only Recipe',
            adjectives='ghost',
            publication_date=date(2025, 11, 17)
        )
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response, '1')
        self.assertContains(response, 'recipe')