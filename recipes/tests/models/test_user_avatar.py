from django.test import TestCase
from recipes.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io


class UserAvatarTestCase(TestCase):
    """Tests for user avatar functionality."""

    def setUp(self):
        """Set up test users."""
        self.user_initials = User.objects.create_user(
            username='@testuser',
            first_name='Test',
            last_name='User',
            email='test@example.com',
            password='Password123',
            avatar_type='initials'
        )

        self.user_ai = User.objects.create_user(
            username='@janedoe',
            first_name='Jane',
            last_name='Doe',
            email='jane@example.com',
            password='Password123',
            avatar_type='ai',
            gender='F',
            age_range='young'
        )

        self.user_random = User.objects.create_user(
            username='@randomuser',
            first_name='Random',
            last_name='Person',
            email='random@example.com',
            password='Password123',
            avatar_type='random',
            avatar_seed='test-seed-123'
        )

    def test_initials_avatar_url(self):
        """Test that initials avatar returns correct URL."""
        avatar_url = self.user_initials.gravatar()
        self.assertIn('ui-avatars.com', avatar_url)
        self.assertIn('background=f15034', avatar_url)

    def test_ai_avatar_url_female(self):
        """Test that AI avatar for female returns women portrait."""
        avatar_url = self.user_ai.gravatar()
        self.assertIn('randomuser.me', avatar_url)
        self.assertIn('women', avatar_url)

    def test_ai_avatar_url_male(self):
        """Test that AI avatar for male returns men portrait."""
        self.user_ai.gender = 'M'
        self.user_ai.save()
        avatar_url = self.user_ai.gravatar()
        self.assertIn('randomuser.me', avatar_url)
        self.assertIn('men', avatar_url)

    def test_random_avatar_url(self):
        """Test that random avatar returns DiceBear URL with seed."""
        avatar_url = self.user_random.gravatar()
        self.assertIn('dicebear.com', avatar_url)
        self.assertIn('test-seed-123', avatar_url)

    def test_uploaded_picture_overrides_avatar_type(self):
        """Test that uploaded picture takes priority over avatar type."""
        # Create a simple test image
        image = Image.new('RGB', (100, 100), color='red')
        image_file = io.BytesIO()
        image.save(image_file, 'PNG')
        image_file.seek(0)

        uploaded_file = SimpleUploadedFile(
            name='test_image.png',
            content=image_file.read(),
            content_type='image/png'
        )

        self.user_initials.profile_picture = uploaded_file
        self.user_initials.save()

        avatar_url = self.user_initials.gravatar()
        self.assertIn('/media/profile_pictures/', avatar_url)

    def test_mini_gravatar_uses_smaller_size(self):
        """Test that mini_gravatar returns smaller image."""
        avatar_url = self.user_initials.mini_gravatar()
        self.assertIn('size=60', avatar_url)

    def test_age_range_affects_ai_avatar(self):
        """Test that different age ranges produce different AI avatars."""
        # Young age range
        self.user_ai.age_range = 'young'
        self.user_ai.save()
        young_url = self.user_ai.gravatar()

        # Senior age range
        self.user_ai.age_range = 'senior'
        self.user_ai.save()
        senior_url = self.user_ai.gravatar()

        # URLs should be different
        self.assertNotEqual(young_url, senior_url)

    def test_avatar_type_default_is_initials(self):
        """Test that new users default to initials avatar type."""
        new_user = User.objects.create_user(
            username='@newbie',
            first_name='New',
            last_name='User',
            email='new@example.com',
            password='Password123'
        )
        self.assertEqual(new_user.avatar_type, 'initials')

    def test_avatar_seed_is_optional(self):
        """Test that avatar_seed can be blank."""
        user = User.objects.create_user(
            username='@noseed',
            first_name='No',
            last_name='Seed',
            email='noseed@example.com',
            password='Password123'
        )
        self.assertEqual(user.avatar_seed, '')

    def tearDown(self):
        """Clean up uploaded files."""
        if self.user_initials.profile_picture:
            self.user_initials.profile_picture.delete()