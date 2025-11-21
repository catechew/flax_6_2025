"""
Tests for the user profile view.
"""
from django.test import TestCase
from django.urls import reverse
from recipes.models import User, Recipe
from datetime import date


class UserProfileViewTestCase(TestCase):
    """Tests for the user_profile view."""

    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        """Set up test data before each test."""
        self.user = User.objects.get(username='@johndoe')
        self.other_user = User.objects.create_user(
            username='@janedoe',
            email='jane@example.org',
            password='Password123',
            first_name='Jane',
            last_name='Doe'
        )
        self.recipe1 = Recipe.objects.create(
            author=self.other_user,
            title='Jane Recipe 1',
            dietary_tags='vegetarian',
            other_tags='delicious, easy',
            publication_date=date(2025, 11, 20)
        )
        self.recipe2 = Recipe.objects.create(
            author=self.other_user,
            title='Jane Recipe 2',
            dietary_tags='healthy',
            publication_date=date(2025, 11, 19)
        )
        self.url = reverse('user_profile', kwargs={'user_id': self.other_user.id})

    def test_user_profile_url(self):
        """Test that the user profile URL is correct."""
        self.assertEqual(self.url, f'/user/{self.other_user.id}/')

    def test_user_profile_redirects_when_not_logged_in(self):
        """Test that viewing profiles requires login."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_user_profile_accessible_when_logged_in(self):
        """Test that logged-in users can view profiles."""
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_user_profile_uses_correct_template(self):
        """Test that the correct template is used."""
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'user_profile.html')

    def test_user_profile_shows_user_information(self):
        """Test that user's information is displayed."""
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response, 'Jane Doe')
        self.assertContains(response, '@janedoe')

    def test_user_profile_shows_user_recipes(self):
        """Test that user's recipes are displayed."""
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response, 'Jane Recipe 1')
        self.assertContains(response, 'Jane Recipe 2')
        self.assertContains(response, 'delicious')
        self.assertContains(response, 'vegetarian')

    def test_user_profile_shows_recipe_count(self):
        """Test that recipe count is accurate."""
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.context['recipe_count'], 2)

    def test_user_profile_shows_follow_button_for_other_users(self):
        """Test that follow button appears on other users' profiles."""
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response, 'Follow')     # Should show follow button
        self.assertNotContains(response, 'Edit Profile')

    def test_user_profile_shows_edit_button_for_own_profile(self):
        """Test that edit button appears on your own profile."""
        self.client.login(username='@johndoe', password='Password123')
        own_url = reverse('user_profile', kwargs={'user_id': self.user.id})
        response = self.client.get(own_url)
        self.assertContains(response, 'Edit Profile')       # Should show edit button
        self.assertNotContains(response, 'follow_user')  # No follow URL
        self.assertNotContains(response, 'unfollow_user')

    def test_user_profile_shows_unfollow_if_already_following(self):
        """Test that unfollow button appears if already following."""
        self.client.login(username='@johndoe', password='Password123')
        self.user.follow(self.other_user)
        response = self.client.get(self.url)
        self.assertContains(response, 'Unfollow')

    def test_user_profile_context_variables(self):
        """Test that context contains required variables."""
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertIn('profile_user', response.context)
        self.assertIn('recipes', response.context)
        self.assertIn('recipe_count', response.context)
        self.assertIn('is_following', response.context)
        self.assertIn('is_own_profile', response.context)
        self.assertEqual(response.context['profile_user'], self.other_user)
        self.assertEqual(response.context['is_own_profile'], False)

    def test_user_profile_with_no_recipes(self):
        """Test profile page when user has no recipes."""
        Recipe.objects.filter(author=self.other_user).delete()
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['recipe_count'], 0)
        self.assertContains(response, "hasn't created any recipes yet")

    def test_user_profile_nonexistent_user(self):
        """Test that viewing non-existent user returns 404."""
        self.client.login(username='@johndoe', password='Password123')
        fake_url = reverse('user_profile', kwargs={'user_id': 99999})
        response = self.client.get(fake_url)
        self.assertEqual(response.status_code, 404)