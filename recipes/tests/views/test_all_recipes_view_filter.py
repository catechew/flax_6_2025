from django.test import TestCase
from django.urls import reverse
from recipes.models import Recipe
from recipes.tests.utils import get_default_user, create_test_recipe


class AllRecipesFilterTestCase(TestCase):
    """tests for filter functionality in all recipes view"""
    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = get_default_user()
        self.url = reverse('all_recipes')
        self.client.login(username='@johndoe', password='Password123')

    def test_filter_by_course_tag(self):
        """test filtering recipes by course tag"""
        Recipe.objects.all().delete()
        breakfast_recipe = create_test_recipe(
            course_tags="breakfast"
        )
    
        dinner_recipe = create_test_recipe(
            course_tags="main"
        )

        response = self.client.get(self.url, {'course': 'breakfast'})
        recipes = list(response.context['recipes'])

        self.assertEqual(response.status_code, 200)
        self.assertIn(breakfast_recipe, recipes)
        self.assertNotIn(dinner_recipe, recipes)

    def test_filter_by_dietary_tag(self):
        """test filtering recipes by dietary tag"""
        Recipe.objects.all().delete()
        vegan_recipe = create_test_recipe(
            dietary_tags="vegan"
        )
        
        non_vegan_recipe = create_test_recipe(
            dietary_tags=""
        )

        response = self.client.get(self.url, {'dietary': 'vegan'})
        recipes = list(response.context['recipes'])

        self.assertEqual(response.status_code, 200)
        self.assertIn(vegan_recipe, recipes)
        self.assertNotIn(non_vegan_recipe, recipes)

    def test_filter_by_cuisine_tag(self):
        """test filtering recipes by cuisine tag"""
        Recipe.objects.all().delete()
        italian_recipe = create_test_recipe(
            cuisine_tags="Italian"
        )
    
        japanese_recipe = create_test_recipe(
            cuisine_tags="Japanese"
        )

        response = self.client.get(self.url, {'cuisine': 'Italian'})
        recipes = list(response.context['recipes'])

        self.assertEqual(response.status_code, 200)
        self.assertIn(italian_recipe, recipes)
        self.assertNotIn(japanese_recipe, recipes)

    def test_filter_by_other_tag(self):
        """test filtering recipes by other tag"""
        Recipe.objects.all().delete()
        quick_recipe = create_test_recipe(
            other_tags="quick"
        )

        slow_recipe = create_test_recipe(
            other_tags=""
        )

        response = self.client.get(self.url, {'other': 'quick'})
        recipes = list(response.context['recipes'])

        self.assertEqual(response.status_code, 200)
        self.assertIn(quick_recipe, recipes)
        self.assertNotIn(slow_recipe, recipes)

    def test_filter_multiple_tags_same_category(self):
        """test filtering with multiple tags from same category"""
        Recipe.objects.all().delete()
        breakfast_recipe = create_test_recipe(
            course_tags="breakfast"
        )
        dessert_recipe = create_test_recipe(
            course_tags="dessert"
        )
        main_recipe = create_test_recipe(
            course_tags="main"
        )

        response = self.client.get(self.url, {'course': ['breakfast', 'dessert']})
        recipes = list(response.context['recipes'])

        self.assertEqual(response.status_code, 200)
        self.assertIn(breakfast_recipe, recipes)
        self.assertIn(dessert_recipe, recipes)
        self.assertNotIn(main_recipe, recipes)

    def test_filter_context_variables(self):
        """test that filter parameters are passed to context"""
        response = self.client.get(self.url, {'course': 'main', 'dietary': 'vegan'})

        self.assertIn('filters', response.context)
        self.assertIn('course_filters', response.context['filters'])
        self.assertIn('dietary_filters', response.context['filters'])
        self.assertIn('main', response.context['filters']['course_filters'])
        self.assertIn('vegan', response.context['filters']['dietary_filters'])

    def test_filter_options_in_context(self):
        """test that filter options are available in context"""
        response = self.client.get(self.url)

        self.assertIn('course_options', response.context)
        self.assertIn('dietary_options', response.context)
        self.assertIn('cuisine_options', response.context)
        self.assertIn('other_options', response.context)