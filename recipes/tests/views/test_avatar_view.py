from django.test import TestCase, Client
from django.urls import reverse
from recipes.models import User


class RandomiseAvatarViewTestCase(TestCase):
    """Tests for randomise_avatar view."""

    def setUp(self):
        """Set up test user and client."""
        self.user = User.objects.create_user(
            username='@testuser',
            first_name='Test',
            last_name='User',
            email='test@example.com',
            password='Password123',
            avatar_type='initials'
        )
        self.client = Client()
        self.url = reverse('randomise_avatar')

    def test_randomise_avatar_requires_login(self):
        """Test that randomise avatar requires authentication."""
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/log_in/', response.url)

    def test_randomise_avatar_generates_seed(self):
        """Test that randomise avatar generates a new seed."""
        self.client.login(username='@testuser', password='Password123')

        # Initially no seed
        self.assertEqual(self.user.avatar_seed, '')

        response = self.client.post(self.url)

        # Refresh from database
        self.user.refresh_from_db()

        # Should have seed now
        self.assertNotEqual(self.user.avatar_seed, '')
        self.assertEqual(self.user.avatar_type, 'random')
        self.assertEqual(response.status_code, 302)

    def test_randomise_avatar_clears_uploaded_picture(self):
        """Test that randomise avatar removes uploaded picture."""
        self.client.login(username='@testuser', password='Password123')

        # Simulate uploaded picture
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.user.profile_picture = SimpleUploadedFile(
            'test.png', b'file_content', content_type='image/png'
        )
        self.user.save()

        response = self.client.post(self.url)

        self.user.refresh_from_db()
        self.assertFalse(self.user.profile_picture)

    def test_randomise_avatar_redirects_to_profile(self):
        """Test that randomise avatar redirects back to profile."""
        self.client.login(username='@testuser', password='Password123')
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('profile'))


class UseInitialsAvatarViewTestCase(TestCase):
    """Tests for use_initials_avatar view."""

    def setUp(self):
        """Set up test user and client."""
        self.user = User.objects.create_user(
            username='@testuser',
            first_name='Test',
            last_name='User',
            email='test@example.com',
            password='Password123',
            avatar_type='random',
            avatar_seed='some-seed'
        )
        self.client = Client()
        self.url = reverse('use_initials_avatar')

    def test_use_initials_requires_login(self):
        """Test that use initials requires authentication."""
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/log_in/', response.url)

    def test_use_initials_sets_avatar_type(self):
        """Test that use initials sets avatar_type to initials."""
        self.client.login(username='@testuser', password='Password123')

        response = self.client.post(self.url)

        self.user.refresh_from_db()

        self.assertEqual(self.user.avatar_type, 'initials')
        self.assertEqual(self.user.avatar_seed, '')
        self.assertEqual(response.status_code, 302)

    def test_use_initials_clears_avatar_seed(self):
        """Test that use initials clears the avatar seed."""
        self.client.login(username='@testuser', password='Password123')

        # User has random avatar
        self.assertNotEqual(self.user.avatar_seed, '')

        response = self.client.post(self.url)

        self.user.refresh_from_db()
        self.assertEqual(self.user.avatar_seed, '')

    def test_use_initials_redirects_to_profile(self):
        """Test that use initials redirects back to profile."""
        self.client.login(username='@testuser', password='Password123')
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('profile'))