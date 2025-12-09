"""
Tests for the My Recipes view.
"""
from django.test import TestCase
from django.urls import reverse
from recipes.models import User, Recipe
from datetime import date
from recipes.tests.utils import get_default_user, create_test_user, create_test_recipe, create_test_recipes


class MyRecipesViewTestCase(TestCase):
    """
    Tests for the my_recipes view.
    """
    
    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        """ Set up test data before each test. """
        self.url = reverse('my_recipes')
        self.user = get_default_user()
        self.recipe1 = create_test_recipe(
            title='Test Recipe One',
            publication_date=date(2025, 11, 17),
            course_tags="breakfast",
            cuisine_tags="Japanese",
            dietary_tags="vegan",
            other_tags="other"
        )
        self.recipe2 = create_test_recipe(
            title='Test Recipe Two',
            publication_date=date(2025, 11, 16),
            course_tags="main",
            cuisine_tags="Italian",
            dietary_tags="vegetarian",
            other_tags="others"
        )
        self.other_user = create_test_user(username='@janedoe')

        self.other_recipe = create_test_recipe(
            author=self.other_user,
            title='Other User Recipe',
            publication_date=date(2025, 11, 15),
        )

    def test_my_recipes_url(self):
        """ Test that the my_recipes URL is correct. """
        self.assertEqual(self.url, '/my_recipes/')

    def test_get_my_recipes_redirects_when_not_logged_in(self):
        """ Test that accessing my_recipes redirects to login when not authenticated. """
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('log_in') + f'?next={self.url}'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_my_recipes_when_logged_in(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_my_recipes_uses_correct_template(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(response, 'users/user_profile.html')

    def test_my_recipes_shows_only_user_recipes(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertContains(response, 'Test Recipe One')
        self.assertContains(response, 'Test Recipe Two')
        self.assertContains(response, 'breakfast')
        self.assertContains(response, 'main')
        self.assertContains(response, 'other')
        self.assertContains(response, 'Japanese')
        self.assertContains(response, 'Italian')
        self.assertContains(response, 'others')
        self.assertNotContains(response, 'Other User Recipe')

    def test_my_recipes_shows_correct_recipe_count(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.context['recipe_count'], 2)

    def test_my_recipes_shows_user_information(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertContains(response, '@johndoe')
        self.assertContains(response, self.user.first_name)
        self.assertContains(response, self.user.last_name)

    def test_my_recipes_with_no_recipes(self):
        """ Test empty page view when user has no recipes. """
        Recipe.objects.visible_to(self.user).delete()
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['recipe_count'], 0)
        self.assertContains(response, "You haven't created any recipes yet")

    def test_my_recipes_displays_recipe_details(self):
        """ Test that recipe details are displayed correctly. """
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertContains(response, 'Test Recipe One')
        self.assertContains(response, 'breakfast')
        self.assertContains(response, 'Japanese')
        self.assertContains(response, 'vegan')    
        self.assertContains(response, 'other')
        self.assertContains(response, 'Nov 17, 2025')

    def test_my_recipes_has_links_to_recipe_actions(self):
        """ Test that view/edit/delete links are present. """
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertContains(response, 'View')
        self.assertContains(response, 'Edit')
        self.assertContains(response, 'Delete')

    def test_my_recipes_shows_create_recipe_link_when_empty(self):
        """ Test that create recipe link appears when no recipes exist. """
        Recipe.objects.visible_to(self.user).delete()
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url, follow=True)
        create_url = reverse('create_recipe')
        self.assertContains(response, create_url)
        self.assertContains(response, 'Create Your First Recipe')

    def test_my_recipes_context_contains_required_data(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertIn('user', response.context)
        self.assertIn('recipes', response.context)
        self.assertIn('recipe_count', response.context)
        self.assertEqual(response.context['user'], self.user)

    def test_my_recipes_with_many_recipes(self):
        create_test_recipes(count=10)
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.context['recipe_count'], 12)
        self.assertEqual(len(response.context['recipes']), 12)

    def test_my_recipes_recipe_ordering(self):
        """ Test that recipes are ordered by publication date (newest first). """
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url, follow=True)
        recipes = list(response.context['recipes'])
        self.assertEqual(recipes[0].title, 'Test Recipe One') #has publication date as 17th
        self.assertEqual(recipes[1].title, 'Test Recipe Two') #has publication date as 16th

    def test_my_recipes_displays_avatar(self):
        """ Test that user's avatar is displayed. """
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertContains(response, 'avatar')

    def test_my_recipes_pluralization(self):
        """ Test that recipe/recipes text is pluralized correctly. """
        Recipe.objects.visible_to(self.user).delete()
        create_test_recipe()
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertContains(response, '1')
        self.assertContains(response, 'recipe')