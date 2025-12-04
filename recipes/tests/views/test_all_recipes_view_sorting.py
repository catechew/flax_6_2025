from django.test import TestCase
from django.urls import reverse
from recipes.models import Recipe, User
from django.utils import timezone
from datetime import timedelta
from recipes.tests.utils import get_default_user, create_test_recipe

class AllRecipesSortTestCase(TestCase):
    """Tests for recipe sorting functionality"""
    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = get_default_user()
        self.url = reverse('all_recipes')
        self.client.login(username="@johndoe", password='Password123')

    def test_sort_by_date_newest(self):
        """Test sorting by newest date first (default)"""
        Recipe.objects.all().delete()
        old_recipe = create_test_recipe(
            publication_date=timezone.now().date() - timedelta(days=5),
        )
        new_recipe = create_test_recipe()        

        response = self.client.get(self.url, {'sort': 'date_newest'})
        recipes = list(response.context['recipes'])

        self.assertEqual(recipes[0], new_recipe)
        self.assertEqual(recipes[1], old_recipe)

    def test_sort_by_date_oldest(self):
        """Test sorting by oldest date first"""
        Recipe.objects.all().delete()
        old_recipe = create_test_recipe(
            publication_date=timezone.now().date() - timedelta(days=5),
        )
        new_recipe = create_test_recipe()

        response = self.client.get(self.url, {'sort': 'date_oldest'})
        recipes = list(response.context['recipes'])

        self.assertEqual(recipes[0], old_recipe)
        self.assertEqual(recipes[1], new_recipe)

    def test_sort_by_prep_time_least(self):
        """Test sorting by least prep time"""
        Recipe.objects.all().delete()
        quick_recipe = create_test_recipe(
            prep_time_hours=0,
            prep_time_minutes=10
        )
        slow_recipe = create_test_recipe(
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
        recipe_z = create_test_recipe(
            title="Zebra Cake",
        )
        recipe_a = create_test_recipe(
            title="Apple Pie",
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
        old_vegan = create_test_recipe(
            publication_date=timezone.now().date() - timedelta(days=5),
            dietary_tags="vegan"
        )
        new_vegan = create_test_recipe(
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
        quick_recipe = create_test_recipe(
            prep_time_hours=0,
            prep_time_minutes=10
        )
        slow_recipe = create_test_recipe(
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
        quick_recipe = create_test_recipe(
            cook_time_hours=0,
            cook_time_minutes=15
        )
        slow_recipe = create_test_recipe(
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
        quick_recipe = create_test_recipe(
            cook_time_hours=0,
            cook_time_minutes=15
        )
        slow_recipe = create_test_recipe(
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
        quick_recipe = create_test_recipe(
            prep_time_hours=0,
            prep_time_minutes=10,
            cook_time_hours=0,
            cook_time_minutes=15
        )
        slow_recipe = create_test_recipe(
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
        recipe_z = create_test_recipe(
            title="Zebra Cake",
        )
        recipe_a = create_test_recipe(
            title="Apple Pie",
        )

        response = self.client.get(self.url, {'sort': 'title_za'})
        recipes = list(response.context['recipes'])

        self.assertEqual(recipes[0], recipe_z)
        self.assertEqual(recipes[1], recipe_a)

    def test_sort_by_invalid_defaults_to_newest(self):
        """Test that invalid sort parameter defaults to newest"""
        Recipe.objects.all().delete()
        old_recipe = create_test_recipe(
            publication_date=timezone.now().date() - timedelta(days=5),
        )
        new_recipe =create_test_recipe()

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
        popular_recipe = create_test_recipe()
        unpopular_recipe = create_test_recipe()

        # Add saves
        popular_recipe.saved_by.add(self.user, user2, user3)
        unpopular_recipe.saved_by.add(self.user)

        response = self.client.get(self.url, {'sort': 'saves_most'})
        recipes = list(response.context['recipes'])

        self.assertEqual(recipes[0], popular_recipe)
        self.assertEqual(recipes[1], unpopular_recipe)