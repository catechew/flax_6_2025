"""
Tests for the follow/unfollow functionality.
"""
from django.test import TestCase
from django.urls import reverse
from recipes.models import User


class FollowViewTestCase(TestCase):
    """ Tests for follow and unfollow views. """

    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        
        self.other_user = User.objects.create_user(
            username='@janedoe',
            email='jane@example.org',
            password='Password123',
            first_name='Jane',
            last_name='Doe'
        )

        self.follow_url = reverse('follow_user', kwargs={'user_id': self.other_user.id})
        self.unfollow_url = reverse('unfollow_user', kwargs={'user_id': self.other_user.id})

    def test_follow_url(self):
        """ Test that the 'follow' URL is correct. """
        self.assertEqual(self.follow_url, f'/user/{self.other_user.id}/follow/')

    def test_unfollow_url(self):
        """ Test that the 'unfollow' URL is correct. """
        self.assertEqual(self.unfollow_url, f'/user/{self.other_user.id}/unfollow/')

    def test_follow_redirects_when_not_logged_in(self):
        """ Test that following requires login. """
        response = self.client.post(self.follow_url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.user.is_following(self.other_user))

    def test_follow_user_successfully(self):
        """ Test that a user can follow another user. """
        self.client.login(username='@johndoe', password='Password123')
        self.assertFalse(self.user.is_following(self.other_user)) 
        response = self.client.post(self.follow_url) 
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db() 
        self.assertTrue(self.user.is_following(self.other_user))

    def test_cannot_follow_yourself(self):
        """ Test that users cannot follow themselves. """
        self.client.login(username='@johndoe', password='Password123')
        self_follow_url = reverse('follow_user', kwargs={'user_id': self.user.id})
        response = self.client.post(self_follow_url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.user.is_following(self.user))

    def test_follow_user_twice_has_no_effect(self):
        """ Test that following an already-followed user doesn't duplicate. """
        self.client.login(username='@johndoe', password='Password123')
        self.user.follow(self.other_user)
        initial_count = self.other_user.follower_count()
        self.client.post(self.follow_url)
        self.assertEqual(self.other_user.follower_count(), initial_count)

    def test_unfollow_user_successfully(self):
        """ Test that a user can unfollow another user. """
        self.client.login(username='@johndoe', password='Password123')
        self.user.follow(self.other_user)   
        self.assertTrue(self.user.is_following(self.other_user))
        response = self.client.post(self.unfollow_url) 
        self.assertEqual(response.status_code, 302)   
        self.user.refresh_from_db()       
        self.assertFalse(self.user.is_following(self.other_user))  

    def test_unfollow_when_not_following(self):
        """ Test that unfollowing when not following doesn't crash. """
        self.client.login(username='@johndoe', password='Password123')
        self.assertFalse(self.user.is_following(self.other_user))
        response = self.client.post(self.unfollow_url)
        self.assertEqual(response.status_code, 302)

    def test_follower_count(self):
        """ Test that follower count is accurate. """
        third_user = User.objects.create_user(
            username='@bobsmith',
            email='bob@example.org',
            password='Password123',
            first_name='Bob',
            last_name='Smith'
        )

        self.assertEqual(self.other_user.follower_count(), 0)
        self.user.follow(self.other_user)
        self.assertEqual(self.other_user.follower_count(), 1)
        third_user.follow(self.other_user)
        self.assertEqual(self.other_user.follower_count(), 2)
        self.user.unfollow(self.other_user)
        self.assertEqual(self.other_user.follower_count(), 1)

    def test_following_count(self):
        """ Test that following count is accurate. """
        third_user = User.objects.create_user(
            username='@bobsmith',
            email='bob@example.org',
            password='Password123',
            first_name='Bob',
            last_name='Smith'
        )

        self.assertEqual(self.user.following_count(), 0)
        self.user.follow(self.other_user)
        self.assertEqual(self.user.following_count(), 1)
        self.user.follow(third_user)
        self.assertEqual(self.user.following_count(), 2)

    def test_follow_nonexistent_user(self):
        """ Test that following a non-existent user returns 404. """
        self.client.login(username='@johndoe', password='Password123')
        fake_url = reverse('follow_user', kwargs={'user_id': 99999})
        response = self.client.post(fake_url)
        self.assertEqual(response.status_code, 404)


class FollowersPageTests(TestCase):
    """ Tests for followers_list and following_list views. """

    def setUp(self):
        self.user = User.objects.create_user(
            username='@alpha',
            email='alpha@example.com',
            password='Password123'
        )
        self.other = User.objects.create_user(
            username='@beta',
            email='beta@example.com',
            password='Password123'
        )

        self.other.follow(self.user)

    def test_followers_list_requires_login(self):
        url = reverse('followers_list', args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_followers_list_logged_in(self):
        self.client.login(username='@alpha', password='Password123')
        url = reverse('followers_list', args=[self.user.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '@beta')

    def test_following_list_requires_login(self):
        url = reverse('following_list', args=[self.other.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_following_list_logged_in(self):
        self.client.login(username='@beta', password='Password123')
        url = reverse('following_list', args=[self.other.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '@alpha')
