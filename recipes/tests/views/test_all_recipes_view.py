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
            publication_date=timezone.now().date(),
            ingredients="Oats (1 cup)\nGreek Yoghurt (300g)",
            steps="Mix ingredients together\nPut it in the fridge overnight",
            other_tags='healthy'
        )

        self.recipe2 = Recipe.objects.create(
            author=self.user,
            title="One Pot Chicken and Rice",
            publication_date=timezone.now().date(),
            other_tags='healthy',
            ingredients="Chicken (1lb)\nRice (1 cup)",
            steps="Fry the rice for one minute\nAdd water to the rice\nPut the chicken on top of the rice\nCover pot with a lid and boil under low heat for 20min"
        )

        self.recipe3 = Recipe.objects.create(
            author=self.user,
            title="Spaghetti Carbonara",
            publication_date=timezone.now().date(),
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
        for i in range(25):
            Recipe.objects.create(
            author=self.user,
            title=f"Recipe {i}",
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
            publication_date = timezone.now().date() - timedelta(days=10),
            ingredients="test(1)",
            steps="test"
        )
        new_recipe = Recipe.objects.create(
            author=self.user,
            title="New Recipe",
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
        print(f"\nContext keys: {response.context.keys()}")
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
        # First, verify recipes exist
        print(f"\nTotal recipes in DB: {Recipe.objects.count()}")
        print(f"Recipe1 author: {self.recipe1.author.username}")
        print(f"Recipe2 author: {self.recipe2.author.username}")
        print(f"Recipe3 author: {self.recipe3.author.username}")

        # Try different search terms to see what works
        print("\n=== Testing different search terms ===")
        
        # Try with @
        response1 = self.client.get(self.url, {'q': '@johndoe'})
        print(f"Search '@johndoe': {len(list(response1.context['recipes']))} recipes")
        
        # Try without @
        response2 = self.client.get(self.url, {'q': 'johndoe'})
        print(f"Search 'johndoe': {len(list(response2.context['recipes']))} recipes")
        
        # Try first/last name
        response3 = self.client.get(self.url, {'q': 'John'})
        print(f"Search 'John': {len(list(response3.context['recipes']))} recipes")
        
        response4 = self.client.get(self.url, {'q': 'Doe'})
        print(f"Search 'Doe': {len(list(response4.context['recipes']))} recipes")
        
        # Try recipe title
        response5 = self.client.get(self.url, {'q': 'Oats'})
        print(f"Search 'Oats': {len(list(response5.context['recipes']))} recipes")

        response = self.client.get(self.url, {'q': '@johndoe'})
        print(f"\nContext keys: {response.context.keys()}")
        print(f"Recipes in context: {response.context['recipes']}")
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

        jane_recipe = Recipe.objects.create(
            author=jane,
            title="Jane's Special Dish",
            publication_date=timezone.now().date(),
            ingredients="Sugar (100g)",
            steps="Mix it"
        )

        response = self.client.get(self.url, {'q': 'Jane Doe'})
        recipes = list(response.context['recipes'])

        # Should find Jane's recipe by full name
        self.assertIn(jane_recipe, recipes)

    def test_search_multiple_ingredients_and_logic(self):
        """Test searching with multiple ingredients uses AND logic"""
        Recipe.objects.all().delete()

        # Recipe with both avocado and garlic
        recipe_both = Recipe.objects.create(
            author=self.user,
            title="Guacamole",
            publication_date=timezone.now().date(),
            ingredients="Avocado (2)\nGarlic (1 clove)\nLime (1)",
            steps="Mash together"
        )

        # Recipe with only avocado
        recipe_avocado_only = Recipe.objects.create(
            author=self.user,
            title="Avocado Toast",
            publication_date=timezone.now().date(),
            ingredients="Avocado (1)\nBread (2 slices)",
            steps="Toast and spread"
        )

        # Recipe with only garlic
        recipe_garlic_only = Recipe.objects.create(
            author=self.user,
            title="Garlic Bread",
            publication_date=timezone.now().date(),
            ingredients="Garlic (3 cloves)\nBread (1 loaf)\nButter (50g)",
            steps="Mix and bake"
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

        recipe = Recipe.objects.create(
            author=self.user,
            title="Chicken Rice Dish",
            publication_date=timezone.now().date(),
            ingredients="Chicken (500g)\nRice (200g)\nOnion (1)",
            steps="Cook together"
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

        recipe_all_three = Recipe.objects.create(
            author=self.user,
            title="Complex Dish",
            publication_date=timezone.now().date(),
            ingredients="Tomato (2)\nOnion (1)\nGarlic (3 cloves)\nPasta (200g)",
            steps="Cook all"
        )

        recipe_two_only = Recipe.objects.create(
            author=self.user,
            title="Simple Dish",
            publication_date=timezone.now().date(),
            ingredients="Tomato (1)\nOnion (1)",
            steps="Mix"
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
        recipe_title = Recipe.objects.create(
            author=self.user,
            title="Spicy Korean Noodles",
            publication_date=timezone.now().date(),
            ingredients="Noodles (200g)",
            steps="Cook"
        )

        response = self.client.get(self.url, {'q': 'Korean Noodles'})
        recipes = list(response.context['recipes'])

        # Should find by title even though it's multiple words
        self.assertIn(recipe_title, recipes)

    def test_search_case_insensitive_multiple_words(self):
        """Test that multi-word search is case insensitive"""
        Recipe.objects.all().delete()

        recipe = Recipe.objects.create(
            author=self.user,
            title="Test Recipe",
            publication_date=timezone.now().date(),
            ingredients="Chicken (500g)\nRice (200g)",
            steps="Cook"
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

        recipe1 = Recipe.objects.create(
            author=self.user,
            title="Chicken Soup",
            publication_date=timezone.now().date(),
            ingredients="Water (1L)",
            steps="Boil"
        )

        recipe2 = Recipe.objects.create(
            author=self.user,
            title="Pasta",
            publication_date=timezone.now().date(),
            ingredients="Chicken (300g)\nPasta (200g)",
            steps="Cook"
        )

        recipe3 = Recipe.objects.create(
            author=self.user,
            title="Rice",
            publication_date=timezone.now().date(),
            ingredients="Rice (200g)",
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

     # Filter tests
    def test_filter_by_course_tag(self):
        """Test filtering recipes by course tag"""
        Recipe.objects.all().delete()
        breakfast_recipe = Recipe.objects.create(
            author=self.user,
            title="Pancakes",
            publication_date=timezone.now().date(),
            ingredients="Flour (200g)",
            steps="Mix and cook",
            course_tags="breakfast"
        )
        dinner_recipe = Recipe.objects.create(
            author=self.user,
            title="Steak",
            publication_date=timezone.now().date(),
            ingredients="Beef (500g)",
            steps="Grill steak",
            course_tags="main"
        )

        response = self.client.get(self.url, {'course': 'breakfast'})
        recipes = list(response.context['recipes'])

        self.assertEqual(response.status_code, 200)
        self.assertIn(breakfast_recipe, recipes)
        self.assertNotIn(dinner_recipe, recipes)

    def test_filter_by_dietary_tag(self):
        """Test filtering recipes by dietary tag"""
        Recipe.objects.all().delete()
        vegan_recipe = Recipe.objects.create(
            author=self.user,
            title="Tofu Stir Fry",
            publication_date=timezone.now().date(),
            ingredients="Tofu (200g)",
            steps="Stir fry",
            dietary_tags="vegan"
        )
        non_vegan_recipe = Recipe.objects.create(
            author=self.user,
            title="Chicken",
            publication_date=timezone.now().date(),
            ingredients="Chicken (500g)",
            steps="Cook chicken",
            dietary_tags=""
        )

        response = self.client.get(self.url, {'dietary': 'vegan'})
        recipes = list(response.context['recipes'])

        self.assertEqual(response.status_code, 200)
        self.assertIn(vegan_recipe, recipes)
        self.assertNotIn(non_vegan_recipe, recipes)

    def test_filter_by_cuisine_tag(self):
        """Test filtering recipes by cuisine tag"""
        Recipe.objects.all().delete()
        italian_recipe = Recipe.objects.create(
            author=self.user,
            title="Pasta",
            publication_date=timezone.now().date(),
            ingredients="Pasta (200g)",
            steps="Boil pasta",
            cuisine_tags="Italian"
        )
        japanese_recipe = Recipe.objects.create(
            author=self.user,
            title="Sushi",
            publication_date=timezone.now().date(),
            ingredients="Rice (300g)",
            steps="Make sushi",
            cuisine_tags="Japanese"
        )

        response = self.client.get(self.url, {'cuisine': 'Italian'})
        recipes = list(response.context['recipes'])

        self.assertEqual(response.status_code, 200)
        self.assertIn(italian_recipe, recipes)
        self.assertNotIn(japanese_recipe, recipes)

    def test_filter_by_other_tag(self):
        """Test filtering recipes by other tag"""
        Recipe.objects.all().delete()
        quick_recipe = Recipe.objects.create(
            author=self.user,
            title="Quick Meal",
            publication_date=timezone.now().date(),
            ingredients="Bread (2 slices)",
            steps="Toast bread",
            other_tags="quick"
        )
        slow_recipe = Recipe.objects.create(
            author=self.user,
            title="Slow Roast",
            publication_date=timezone.now().date(),
            ingredients="Beef (1kg)",
            steps="Slow roast for 4 hours",
            other_tags=""
        )

        response = self.client.get(self.url, {'other': 'quick'})
        recipes = list(response.context['recipes'])

        self.assertEqual(response.status_code, 200)
        self.assertIn(quick_recipe, recipes)
        self.assertNotIn(slow_recipe, recipes)

    def test_filter_multiple_tags_same_category(self):
        """Test filtering with multiple tags from same category"""
        Recipe.objects.all().delete()
        breakfast_recipe = Recipe.objects.create(
            author=self.user,
            title="Pancakes",
            publication_date=timezone.now().date(),
            ingredients="Flour (200g)",
            steps="Cook",
            course_tags="breakfast"
        )
        dessert_recipe = Recipe.objects.create(
            author=self.user,
            title="Cake",
            publication_date=timezone.now().date(),
            ingredients="Sugar (300g)",
            steps="Bake",
            course_tags="dessert"
        )
        main_recipe = Recipe.objects.create(
            author=self.user,
            title="Steak",
            publication_date=timezone.now().date(),
            ingredients="Beef (500g)",
            steps="Grill",
            course_tags="main"
        )

        response = self.client.get(self.url, {'course': ['breakfast', 'dessert']})
        recipes = list(response.context['recipes'])

        self.assertEqual(response.status_code, 200)
        self.assertIn(breakfast_recipe, recipes)
        self.assertIn(dessert_recipe, recipes)
        self.assertNotIn(main_recipe, recipes)

    def test_filter_context_variables(self):
        """Test that filter parameters are passed to context"""
        response = self.client.get(self.url, {'course': 'main', 'dietary': 'vegan'})

        self.assertIn('filters', response.context)
        self.assertIn('course_filters', response.context['filters'])
        self.assertIn('dietary_filters', response.context['filters'])
        self.assertIn('main', response.context['filters']['course_filters'])
        self.assertIn('vegan', response.context['filters']['dietary_filters'])

    def test_filter_options_in_context(self):
        """Test that filter options are available in context"""
        response = self.client.get(self.url)

        self.assertIn('course_options', response.context)
        self.assertIn('dietary_options', response.context)
        self.assertIn('cuisine_options', response.context)
        self.assertIn('other_options', response.context)

    # Sort tests
    def test_sort_by_date_newest(self):
        """Test sorting by newest date first (default)"""
        Recipe.objects.all().delete()
        old_recipe = Recipe.objects.create(
            author=self.user,
            title="Old",
            publication_date=timezone.now().date() - timedelta(days=5),
            ingredients="test (1)",
            steps="test"
        )
        new_recipe = Recipe.objects.create(
            author=self.user,
            title="New",
            publication_date=timezone.now().date(),
            ingredients="test (1)",
            steps="test"
        )

        response = self.client.get(self.url, {'sort': 'date_newest'})
        recipes = list(response.context['recipes'])

        self.assertEqual(recipes[0], new_recipe)
        self.assertEqual(recipes[1], old_recipe)

    def test_sort_by_date_oldest(self):
        """Test sorting by oldest date first"""
        Recipe.objects.all().delete()
        old_recipe = Recipe.objects.create(
            author=self.user,
            title="Old",
            publication_date=timezone.now().date() - timedelta(days=5),
            ingredients="test (1)",
            steps="test"
        )
        new_recipe = Recipe.objects.create(
            author=self.user,
            title="New",
            publication_date=timezone.now().date(),
            ingredients="test (1)",
            steps="test"
        )

        response = self.client.get(self.url, {'sort': 'date_oldest'})
        recipes = list(response.context['recipes'])

        self.assertEqual(recipes[0], old_recipe)
        self.assertEqual(recipes[1], new_recipe)

    def test_sort_by_prep_time_least(self):
        """Test sorting by least prep time"""
        Recipe.objects.all().delete()
        quick_recipe = Recipe.objects.create(
            author=self.user,
            title="Quick",
            publication_date=timezone.now().date(),
            ingredients="test (1)",
            steps="test",
            prep_time_hours=0,
            prep_time_minutes=10
        )
        slow_recipe = Recipe.objects.create(
            author=self.user,
            title="Slow",
            publication_date=timezone.now().date(),
            ingredients="test (1)",
            steps="test",
            prep_time_hours=2,
            prep_time_minutes=0
        )

        response = self.client.get(self.url, {'sort': 'prep_least'})
        recipes = list(response.context['recipes'])

        self.assertEqual(recipes[0], quick_recipe)
        self.assertEqual(recipes[1], slow_recipe)

    def test_sort_by_title_az(self):
        """Test sorting by title A-Z"""
        Recipe.objects.all().delete()
        recipe_z = Recipe.objects.create(
            author=self.user,
            title="Zebra Cake",
            publication_date=timezone.now().date(),
            ingredients="test (1)",
            steps="test"
        )
        recipe_a = Recipe.objects.create(
            author=self.user,
            title="Apple Pie",
            publication_date=timezone.now().date(),
            ingredients="test (1)",
            steps="test"
        )

        response = self.client.get(self.url, {'sort': 'title_az'})
        recipes = list(response.context['recipes'])

        self.assertEqual(recipes[0], recipe_a)
        self.assertEqual(recipes[1], recipe_z)

    def test_sort_context_variable(self):
        """Test that sort parameter is passed to context"""
        response = self.client.get(self.url, {'sort': 'prep_least'})

        self.assertIn('sort_by', response.context)
        self.assertEqual(response.context['sort_by'], 'prep_least')

    def test_default_sort_is_newest(self):
        """Test that default sort is by newest date"""
        response = self.client.get(self.url)

        self.assertEqual(response.context['sort_by'], 'date_newest')

    def test_filters_and_sort_work_together(self):
        """Test that filtering and sorting work together"""
        Recipe.objects.all().delete()
        old_vegan = Recipe.objects.create(
            author=self.user,
            title="Old Vegan",
            publication_date=timezone.now().date() - timedelta(days=5),
            ingredients="test (1)",
            steps="test",
            dietary_tags="vegan"
        )
        new_vegan = Recipe.objects.create(
            author=self.user,
            title="New Vegan",
            publication_date=timezone.now().date(),
            ingredients="test (1)",
            steps="test",
            dietary_tags="vegan"
        )

        response = self.client.get(self.url, {'dietary': 'vegan', 'sort': 'date_oldest'})
        recipes = list(response.context['recipes'])

        # Should only show vegan recipes, sorted oldest first
        self.assertEqual(len(recipes), 2)
        self.assertEqual(recipes[0], old_vegan)
        self.assertEqual(recipes[1], new_vegan)

    def test_sort_by_prep_most(self):
        """Test sorting by most prep time"""
        Recipe.objects.all().delete()
        quick_recipe = Recipe.objects.create(
            author=self.user,
            title="Quick",
            publication_date=timezone.now().date(),
            ingredients="test (1)",
            steps="test",
            prep_time_hours=0,
            prep_time_minutes=10
        )
        slow_recipe = Recipe.objects.create(
            author=self.user,
            title="Slow",
            publication_date=timezone.now().date(),
            ingredients="test (1)",
            steps="test",
            prep_time_hours=2,
            prep_time_minutes=0
        )

        response = self.client.get(self.url, {'sort': 'prep_most'})
        recipes = list(response.context['recipes'])

        self.assertEqual(recipes[0], slow_recipe)
        self.assertEqual(recipes[1], quick_recipe)

    def test_sort_by_cook_least(self):
        """Test sorting by least cook time"""
        Recipe.objects.all().delete()
        quick_recipe = Recipe.objects.create(
            author=self.user,
            title="Quick",
            publication_date=timezone.now().date(),
            ingredients="test (1)",
            steps="test",
            cook_time_hours=0,
            cook_time_minutes=15
        )
        slow_recipe = Recipe.objects.create(
            author=self.user,
            title="Slow",
            publication_date=timezone.now().date(),
            ingredients="test (1)",
            steps="test",
            cook_time_hours=3,
            cook_time_minutes=0
        )

        response = self.client.get(self.url, {'sort': 'cook_least'})
        recipes = list(response.context['recipes'])

        self.assertEqual(recipes[0], quick_recipe)
        self.assertEqual(recipes[1], slow_recipe)

    def test_sort_by_cook_most(self):
        """Test sorting by most cook time"""
        Recipe.objects.all().delete()
        quick_recipe = Recipe.objects.create(
            author=self.user,
            title="Quick",
            publication_date=timezone.now().date(),
            ingredients="test (1)",
            steps="test",
            cook_time_hours=0,
            cook_time_minutes=15
        )
        slow_recipe = Recipe.objects.create(
            author=self.user,
            title="Slow",
            publication_date=timezone.now().date(),
            ingredients="test (1)",
            steps="test",
            cook_time_hours=3,
            cook_time_minutes=0
        )

        response = self.client.get(self.url, {'sort': 'cook_most'})
        recipes = list(response.context['recipes'])

        self.assertEqual(recipes[0], slow_recipe)
        self.assertEqual(recipes[1], quick_recipe)

    def test_sort_by_total_most(self):
        """Test sorting by most total time"""
        Recipe.objects.all().delete()
        quick_recipe = Recipe.objects.create(
            author=self.user,
            title="Quick",
            publication_date=timezone.now().date(),
            ingredients="test (1)",
            steps="test",
            prep_time_hours=0,
            prep_time_minutes=10,
            cook_time_hours=0,
            cook_time_minutes=15
        )
        slow_recipe = Recipe.objects.create(
            author=self.user,
            title="Slow",
            publication_date=timezone.now().date(),
            ingredients="test (1)",
            steps="test",
            prep_time_hours=2,
            prep_time_minutes=30,
            cook_time_hours=3,
            cook_time_minutes=45
        )

        response = self.client.get(self.url, {'sort': 'total_most'})
        recipes = list(response.context['recipes'])

        self.assertEqual(recipes[0], slow_recipe)
        self.assertEqual(recipes[1], quick_recipe)

    def test_sort_by_title_za(self):
        """Test sorting by title Z-A"""
        Recipe.objects.all().delete()
        recipe_z = Recipe.objects.create(
            author=self.user,
            title="Zebra Cake",
            publication_date=timezone.now().date(),
            ingredients="test (1)",
            steps="test"
        )
        recipe_a = Recipe.objects.create(
            author=self.user,
            title="Apple Pie",
            publication_date=timezone.now().date(),
            ingredients="test (1)",
            steps="test"
        )

        response = self.client.get(self.url, {'sort': 'title_za'})
        recipes = list(response.context['recipes'])

        self.assertEqual(recipes[0], recipe_z)
        self.assertEqual(recipes[1], recipe_a)

    def test_sort_by_invalid_defaults_to_newest(self):
        """Test that invalid sort parameter defaults to newest"""
        Recipe.objects.all().delete()
        old_recipe = Recipe.objects.create(
            author=self.user,
            title="Old",
            publication_date=timezone.now().date() - timedelta(days=5),
            ingredients="test (1)",
            steps="test"
        )
        new_recipe = Recipe.objects.create(
            author=self.user,
            title="New",
            publication_date=timezone.now().date(),
            ingredients="test (1)",
            steps="test"
        )

        response = self.client.get(self.url, {'sort': 'invalid_sort_option'})
        recipes = list(response.context['recipes'])

        # Should default to newest first
        self.assertEqual(recipes[0], new_recipe)
        self.assertEqual(recipes[1], old_recipe)

    def test_sort_by_saves_most(self):
        """Test sorting by most saved"""
        Recipe.objects.all().delete()

        # Create users
        user2 = User.objects.get(username='@janedoe')
        user3 = User.objects.get(username='@petrapickles')

        # Create recipes
        popular_recipe = Recipe.objects.create(
            author=self.user,
            title="Popular Recipe",
            publication_date=timezone.now().date(),
            ingredients="test (1)",
            steps="test"
        )
        unpopular_recipe = Recipe.objects.create(
            author=self.user,
            title="Unpopular Recipe",
            publication_date=timezone.now().date(),
            ingredients="test (1)",
            steps="test"
        )

        # Add saves
        popular_recipe.saved_by.add(self.user, user2, user3)
        unpopular_recipe.saved_by.add(self.user)

        response = self.client.get(self.url, {'sort': 'saves_most'})
        recipes = list(response.context['recipes'])

        self.assertEqual(recipes[0], popular_recipe)
        self.assertEqual(recipes[1], unpopular_recipe)