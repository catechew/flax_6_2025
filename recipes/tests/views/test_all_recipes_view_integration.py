from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from recipes.models import Recipe
from recipes.tests.utils import get_default_user, create_test_recipe


class AllRecipesIntegrationTestCase(TestCase):
    """tests for combined functionality (search + filter + sort)"""
    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = get_default_user()
        self.url = reverse('all_recipes')
        self.client.login(username='@johndoe', password='Password123')

    def test_filters_and_sort_work_together(self):
        """test that filtering and sorting work together"""
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

        self.assertEqual(len(recipes), 2)
        self.assertEqual(recipes[0], old_vegan)
        self.assertEqual(recipes[1], new_vegan)