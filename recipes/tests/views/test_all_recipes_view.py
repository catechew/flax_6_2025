from django.test import TestCase
from django.urls import reverse
from recipes.models import Recipe, User
from django.utils import timezone

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

    def test_pagination_works(self):
        # Create extra recipes to exceed 25 items 
        for i in range(55):
            Recipe.objects.create(
                author=self.user,
                title=f"Recipe {i}",
                adjectives="test",
                publication_date=timezone.now().date()
            )
        
        response = self.client.get(self.url)
        self.assertEqual(response.context['page_object'].paginator.num_pages, 3)