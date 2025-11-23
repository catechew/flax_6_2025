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

        self.assertIn('course_filters', response.context)
        self.assertIn('dietary_filters', response.context)
        self.assertIn('main', response.context['course_filters'])
        self.assertIn('vegan', response.context['dietary_filters'])

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
