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
            publication_date=timezone.now().date(),
            ingredients="Oats (1 cup)\nGreek Yoghurt (300g)",
            steps="Mix ingredients together\nPut it in the fridge overnight"
        )

        self.recipe2 = Recipe.objects.create(
            author=self.user,
            title="One Pot Chicken and Rice",
            adjectives = "protein healthy",
            publication_date=timezone.now().date(),
            ingredients="Chicken (1lb)\nRice (1 cup)",
            steps="Fry the rice for one minute\nAdd water to the rice\nPut the chicken on top of the rice\nCover pot with a lid and boil under low heat for 20min"
        )

        self.recipe3 = Recipe.objects.create(
            author=self.user,
            title="Spaghetti Carbonara",
            adjectives="Italian quick",
            publication_date=timezone.now().date(),
            ingredients="Spaghetti (200g)\nEggs (2)\nCheese (200g)",
            steps="Cook the spaghetti in salted water for 9 min\nDrain the water and mix the eggs and cheese in while still hot"
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
        self.assertIn(self.recipe3, recipes)
    
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
            publication_date=timezone.now().date(),
            ingredients="test(1)",
            steps="test"
        )
        response = self.client.get(self.url)
        self.assertEqual(response.context['page_object'].paginator.num_pages, 1)
        self.assertFalse(response.context['page_object'].has_other_pages())

    def test_all_recipes_with_26_recipes(self):
        Recipe.objects.all().delete()
        for i in range(26):
            Recipe.objects.create(
                author=self.user,
                title=f"Recipe {i}",
                adjectives="test",
                publication_date=timezone.now().date(),
                ingredients="test(1)",
                steps="test"
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
            publication_date = timezone.now().date() - timedelta(days=10),
            ingredients="test(1)",
            steps="test"
        )
        new_recipe = Recipe.objects.create(
            author=self.user,
            title="New Recipe",
            adjectives="new",
            publication_date=timezone.now().date(),
            ingredients="test(1)",
            steps="test"
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
                publication_date=timezone.now().date(),
                ingredients="test(1)",
                steps="test"
            )
        response = self.client.get(self.url)
        self.assertEqual(response.context['page_object'].paginator.num_pages, 3)
        self.assertEqual(response.context['page_object'].paginator.count, 55)

    def test_invalid_page_number(self):
        """Test handling of invalid page parameter"""
        response = self.client.get(self.url + '?page=999')
        self.assertEqual(response.status_code, 200)  # Should show last page
    
    def test_non_numeric_page_parameter(self):
        """Test handling of non-numeric page parameter"""
        response = self.client.get(self.url + '?page=abc')
        self.assertEqual(response.status_code, 200)  # Should show first page

    # Test search functionality
    # Test searching recipes by title
    def test_search_by_title(self):
        response = self.client.get(self.url, {'q': 'Oats'})
        self.assertEqual(response.status_code, 200)
        recipes = list(response.context['recipes'])
        self.assertIn(self.recipe1, recipes)
        self.assertNotIn(self.recipe2, recipes)
        self.assertNotIn(self.recipe3, recipes)
        self.assertEqual(response.context['total_count'], 1)
    
    # Test that search is case insensitive
    def test_search_case_insensitive(self):
        response = self.client.get(self.url, {'q': 'oAtS'})
        recipes = list(response.context['recipes'])
        self.assertIn(self.recipe1, recipes)

        response = self.client.get(self.url, {'q': 'OATS'})
        recipes = list(response.context['recipes'])
        self.assertIn(self.recipe1, recipes)

        response = self.client.get(self.url, {'q': 'oats'})
        recipes = list(response.context['recipes'])
        self.assertIn(self.recipe1, recipes)

    # Test searching recipes by adjectives
    def test_search_by_adjectives(self):
        response = self.client.get(self.url, {'q': 'Italian'})
        self.assertEqual(response.status_code, 200)
        recipes = list(response.context['recipes'])
        self.assertIn(self.recipe3, recipes)
        self.assertNotIn(self.recipe1, recipes)
        self.assertNotIn(self.recipe2, recipes)

    # Test searching recipes by ingredient
    def test_search_by_ingredients(self):
        response = self.client.get(self.url, {'q': 'Yoghurt'})
        self.assertEqual(response.status_code, 200)
        recipes = list(response.context['recipes'])
        self.assertIn(self.recipe1, recipes)
        self.assertNotIn(self.recipe2, recipes)
        self.assertNotIn(self.recipe3, recipes)

    # Test searching recipes by steps
    def test_search_by_steps(self):
        response = self.client.get(self.url, {'q': 'water'})
        self.assertEqual(response.status_code, 200)
        recipes = list(response.context['recipes'])
        self.assertNotIn(self.recipe1, recipes)
        self.assertIn(self.recipe2, recipes)
        self.assertIn(self.recipe3, recipes)

    # Test partial match search
    def test_search_partial_match(self):
        response = self.client.get(self.url, {'q': 'Chick'})
        recipes = list(response.context['recipes'])
        self.assertIn(self.recipe2, recipes) # Matches "Chicken"

    # Test search with no results
    def test_search_no_results(self):
        response = self.client.get(self.url, {'q': 'NonExistent'})
        self.assertEqual(response.status_code, 200)
        recipes = list(response.context['recipes'])
        self.assertEqual(len(recipes), 0)
        self.assertEqual(response.context['total_count'], 0)

    # Test empty search query (returns all recipes)
    def test_empty_search_query(self):
        response = self.client.get(self.url, {'q': ''})
        recipes = list(response.context['recipes'])
        self.assertEqual(len(recipes), 3)
        self.assertIn(self.recipe1, recipes)
        self.assertIn(self.recipe2, recipes)
        self.assertIn(self.recipe3, recipes)

    # Test search whitespace only query (returns all recipes)
    def test_whitespace_search_query(self):
        response = self.client.get(self.url, {'q': '   '})
        recipes = list(response.context['recipes'])
        self.assertEqual(len(recipes), 3)
        self.assertIn(self.recipe1, recipes)
        self.assertIn(self.recipe2, recipes)
        self.assertIn(self.recipe3, recipes)
    
    # Test search query is passed to template context
    def test_search_query_in_context(self):
        response = self.client.get(self.url, {'q': 'Oats'})
        self.assertEqual(response.context['search_query'], 'Oats')  

    # Test search query appears in rendered template   
    def test_search_query_in_rendered_template(self):
        response = self.client.get(self.url, {'q': 'Oats'})
        self.assertContains(response, 'Oats')
        self.assertContains(response, 'Search results for ')

    # Test search that matches multiple recipes
    def test_search_multiple_matches(self):
        response = self.client.get(self.url, {'q': 'healthy'})
        recipes = list(response.context['recipes'])
        self.assertEqual(len(recipes), 2)
        self.assertIn(self.recipe1, recipes)
        self.assertIn(self.recipe2, recipes)
        self.assertNotIn(self.recipe3, recipes)

    # Test that accessing URL without search parameter shows all recipes
    def test_all_recipes_without_search_parameter(self):
        response = self.client.get(self.url)
        recipes = list(response.context['recipes'])
        self.assertEqual(len(recipes), 3)
        self.assertEqual(response.context['search_query'], '')

    # Test that all necessary context variables are present during search
    def test_search_context_variables(self):
        response = self.client.get(self.url, {'q': 'Oats'})
        self.assertIn('recipes', response.context)
        self.assertIn('search_query', response.context)
        self.assertIn('total_count', response.context)
        self.assertIn('user', response.context)
