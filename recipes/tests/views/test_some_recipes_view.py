"""
Tests for the some_recipes view.

Covers:
- Valid recipe IDs
- Empty and missing ID parameters
- Pagination behaviour
- Login requirement
"""

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from recipes.models import Recipe, User


class SomeRecipesViewTestCase(TestCase):
    """
    Tests for displaying specific recipes using ID list.
    """

    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.client.login(username='@johndoe', password='Password123')
        self.url = reverse('some_recipes')

        self.recipe1 = Recipe.objects.create(
            author=self.user,
            title="Recipe One",
            publication_date=timezone.now().date(),
            ingredients="Test",
            steps="Test"
        )
        self.recipe2 = Recipe.objects.create(
            author=self.user,
            title="Recipe Two",
            publication_date=timezone.now().date(),
            ingredients="Test",
            steps="Test"
        )

    def test_login_required(self):
        """ Unauthenticated users are redirected. """
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_valid_ids_return_recipes(self):
        """ Valid IDs return matching recipes. """
        ids = f"{self.recipe1.id},{self.recipe2.id}"
        response = self.client.get(self.url, {'ids': ids})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Recipe One")
        self.assertContains(response, "Recipe Two")

    def test_missing_ids_returns_empty_list(self):
        """ Missing IDs parameter returns no recipes. """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['recipes']), 0)

    def test_empty_ids_returns_empty_list(self):
        """ Empty ids string returns no recipes. """
        response = self.client.get(self.url, {'ids': ''})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['recipes']), 0)

    def test_invalid_ids_are_ignored(self):
        """ Invalid ID strings do not crash the view. """
        response = self.client.get(self.url, {'ids': 'abc,123'})

        self.assertEqual(response.status_code, 200)

    def test_pagination_applied(self):
        """  Pagination limits recipes to 25 per page. """
        Recipe.objects.all().delete()

        recipe_ids = []
        for i in range(30):
            recipe = Recipe.objects.create(
                author=self.user,
                title=f"Recipe {i}",
                publication_date=timezone.now().date(),
                ingredients="Test",
                steps="Test"
            )
            recipe_ids.append(str(recipe.id))

        response = self.client.get(
            self.url, {'ids': ",".join(recipe_ids)}
        )

        page = response.context['page_object']
        self.assertEqual(page.paginator.per_page, 25)
        self.assertTrue(page.has_next())

    def test_correct_template_used(self):
        """ View renders the correct template. """
        response = self.client.get(
            self.url, {'ids': str(self.recipe1.id)}
        )
        self.assertTemplateUsed(response, 'ai/some_recipes.html')
