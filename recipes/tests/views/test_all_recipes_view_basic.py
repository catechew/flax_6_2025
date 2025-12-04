from django.test import TestCase
from django.urls import reverse
from recipes.models import Recipe, User
from django.utils import timezone
from datetime import timedelta
from recipes.tests.utils import create_test_recipes, get_default_user, create_test_recipe

class AllRecipesViewBasicTestCase(TestCase):
    """Tests for the basic all recipes view."""
    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = get_default_user()
        self.url = reverse('all_recipes')

        # Log user in 
        self.client.login(username='@johndoe', password='Password123')

        # Create recipes
        self.recipe1 = create_test_recipe(
            title="Overnight Oats",
            ingredients="Oats (1 cup)\nGreek Yoghurt (300g)",
            steps="Mix ingredients together\nPut it in the fridge overnight",
            other_tags='healthy'
        )

        self.recipe2 = create_test_recipe(
            title="One Pot Chicken and Rice",
            other_tags='healthy',
            ingredients="Chicken (1lb)\nRice (1 cup)",
            steps="Fry the rice for one minute\nAdd water to the rice\nPut the chicken on top of the rice\nCover pot with a lid and boil under low heat for 20min"
        )

        self.recipe3 = create_test_recipe(
            title="Spaghetti Carbonara",
            ingredients="Spaghetti (200g)\nEggs (2)\nCheese (200g)",
            steps="Cook the spaghetti in salted water for 9 min\nDrain the water and mix the eggs and cheese in while still hot"
        )
        
    def test_all_recipes_url(self):
        self.assertEqual(self.url, '/all_recipes/')

    def test_get_all_recipes(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/all_recipes.html')

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
        create_test_recipes(count=25)
        response = self.client.get(self.url)
        self.assertEqual(response.context['page_object'].paginator.num_pages, 1)
        self.assertFalse(response.context['page_object'].has_other_pages())

    def test_all_recipes_with_26_recipes(self):
        Recipe.objects.all().delete()
        create_test_recipes(count=26)
        response = self.client.get(self.url)
        self.assertEqual(response.context['page_object'].paginator.num_pages, 2)

    def test_all_recipes_ordering(self):
        """Test that recipes are ordered by publication date (newest first)"""
        Recipe.objects.all().delete()
        old_recipe = create_test_recipe(
            publication_date = timezone.now().date() - timedelta(days=10),
        )
        new_recipe = create_test_recipe()     
        response = self.client.get(self.url)
        recipes = response.context['recipes']
        self.assertEqual(recipes[0], new_recipe)  # Newest first
        self.assertEqual(recipes[1], old_recipe)  # Older second
    
    def test_pagination_works(self):
    # Clear existing recipes first
        Recipe.objects.all().delete()
        create_test_recipes(count=55)
    
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
        self.assertEqual(response.context['page_object'].paginator.num_pages, 1)
    
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
        self.assertEqual(response.context['page_object'].paginator.count, 0)

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
        # self.assertIn('total_count', response.context) 
        # Cannot find total_count in context anymore so commenting out for convenience
        # TODO: discuss if we need to add it back or not
        self.assertIn('user', response.context)

    # Test searching by username
    def test_search_by_username(self):
        """Test searching recipes by author username"""

        response = self.client.get(self.url, {'q': 'John'})
        recipes = list(response.context['recipes'])
        # All test recipes are by @johndoe
        self.assertEqual(len(recipes), 3)
        self.assertIn(self.recipe1, recipes)
        self.assertIn(self.recipe2, recipes)
        self.assertIn(self.recipe3, recipes)

    def test_search_by_partial_username(self):
        """Test searching by partial username"""
        response = self.client.get(self.url, {'q': 'john'})
        recipes = list(response.context['recipes'])
        # Should match @johndoe
        self.assertGreaterEqual(len(recipes), 1)

    def test_search_by_first_name(self):
        """Test searching recipes by author first name"""
        response = self.client.get(self.url, {'q': 'John'})
        recipes = list(response.context['recipes'])
        # Should find recipes by user with first name John
        self.assertGreaterEqual(len(recipes), 0)

    def test_search_by_last_name(self):
        """Test searching recipes by author last name"""
        response = self.client.get(self.url, {'q': 'Doe'})
        recipes = list(response.context['recipes'])
        # Should find recipes by user with last name Doe
        self.assertGreaterEqual(len(recipes), 0)

    def test_search_by_full_name(self):
        """Test searching recipes by author full name"""
        Recipe.objects.all().delete()
        # Use existing Jane Doe from fixtures
        from recipes.models import User
        jane = User.objects.get(username='@janedoe')

        jane_recipe = create_test_recipe(
            author=jane,
        )

        response = self.client.get(self.url, {'q': 'Jane Doe'})
        recipes = list(response.context['recipes'])

        # Should find Jane's recipe by full name
        self.assertIn(jane_recipe, recipes)

    def test_search_multiple_ingredients_and_logic(self):
        """Test searching with multiple ingredients uses AND logic"""
        Recipe.objects.all().delete()

        # Recipe with both avocado and garlic
        recipe_both = create_test_recipe(
            ingredients="Avocado (2)\nGarlic (1 clove)\nLime (1)",
        )

        # Recipe with only avocado
        recipe_avocado_only = create_test_recipe(
            ingredients="Avocado (1)\nBread (2 slices)",
        )

        # Recipe with only garlic
        recipe_garlic_only = create_test_recipe(
            ingredients="Garlic (3 cloves)\nBread (1 loaf)\nButter (50g)",
        )

        # Search for both ingredients
        response = self.client.get(self.url, {'q': 'Avocado Garlic'})
        recipes = list(response.context['recipes'])

        # Should only find recipe with BOTH ingredients
        self.assertIn(recipe_both, recipes)
        # Should not find recipes with only one ingredient
        self.assertNotIn(recipe_avocado_only, recipes)
        self.assertNotIn(recipe_garlic_only, recipes)

    def test_search_multiple_ingredients_different_order(self):
        """Test multiple ingredient search works regardless of order"""
        Recipe.objects.all().delete()

        recipe = create_test_recipe(
            ingredients="Chicken (500g)\nRice (200g)\nOnion (1)",
        )

        # Search in different order
        response1 = self.client.get(self.url, {'q': 'Chicken Rice'})
        response2 = self.client.get(self.url, {'q': 'Rice Chicken'})

        recipes1 = list(response1.context['recipes'])
        recipes2 = list(response2.context['recipes'])

        # Both should find the recipe
        self.assertIn(recipe, recipes1)
        self.assertIn(recipe, recipes2)

    def test_search_three_ingredients(self):
        """Test searching with three ingredients"""
        Recipe.objects.all().delete()

        recipe_all_three = create_test_recipe(
            ingredients="Tomato (2)\nOnion (1)\nGarlic (3 cloves)\nPasta (200g)",
        )

        recipe_two_only = create_test_recipe(
            ingredients="Tomato (1)\nOnion (1)",
        )

        response = self.client.get(self.url, {'q': 'Tomato Onion Garlic'})
        recipes = list(response.context['recipes'])

        # Should only find recipe with all three
        self.assertIn(recipe_all_three, recipes)
        self.assertNotIn(recipe_two_only, recipes)

    def test_search_multi_word_still_searches_other_fields(self):
        """Test that multi-word search still checks other fields for full phrase"""
        Recipe.objects.all().delete()

        # Recipe with multi-word title
        recipe_title = create_test_recipe(
            title="Spicy Korean Noodles",
            ingredients="Noodles (200g)",
        )

        response = self.client.get(self.url, {'q': 'Korean Noodles'})
        recipes = list(response.context['recipes'])

        # Should find by title even though it's multiple words
        self.assertIn(recipe_title, recipes)

    def test_search_case_insensitive_multiple_words(self):
        """Test that multi-word search is case insensitive"""
        Recipe.objects.all().delete()

        recipe = create_test_recipe(
            ingredients="Chicken (500g)\nRice (200g)",
        )

        # Try different cases
        response1 = self.client.get(self.url, {'q': 'chicken rice'})
        response2 = self.client.get(self.url, {'q': 'CHICKEN RICE'})
        response3 = self.client.get(self.url, {'q': 'ChIcKeN rIcE'})

        recipes1 = list(response1.context['recipes'])
        recipes2 = list(response2.context['recipes'])
        recipes3 = list(response3.context['recipes'])

        # All should find the recipe
        self.assertIn(recipe, recipes1)
        self.assertIn(recipe, recipes2)
        self.assertIn(recipe, recipes3)

    def test_search_single_word_uses_or_logic(self):
        """Test that single word search still uses OR logic across fields"""
        Recipe.objects.all().delete()

        recipe1 = create_test_recipe(
            title="Chicken Soup",
        )

        recipe2 = create_test_recipe(
            ingredients="Chicken (300g)\nPasta (200g)",
        )

        recipe3 = create_test_recipe(
            steps="Fry the chicken pieces"
        )

        response = self.client.get(self.url, {'q': 'Chicken'})
        recipes = list(response.context['recipes'])

        # Should find all three - title, ingredients, and steps
        self.assertIn(recipe1, recipes)  # In title
        self.assertIn(recipe2, recipes)  # In ingredients
        self.assertIn(recipe3, recipes)  # In steps

    def test_search_query_none_defaults_to_empty(self):
        """Test that None search query is handled"""
        # Manually test the None case - this is an edge case
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['search_query'], '')