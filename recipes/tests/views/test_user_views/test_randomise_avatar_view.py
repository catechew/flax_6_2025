from django.test import TestCase, Client
from django.urls import reverse
from recipes.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io


class RandomiseAvatarViewTestCase(TestCase):
    """
    Tests for randomise_avatar and use_initials_avatar views.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="@testuser",
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password="Password123",
            avatar_type="initials",
        )
        self.client.login(username="@testuser", password="Password123")

    def create_test_image(self):
        image = Image.new("RGB", (100, 100), color="red")
        image_file = io.BytesIO()
        image.save(image_file, "PNG")
        image_file.seek(0)

        return SimpleUploadedFile(
            name="test_image.png", content=image_file.read(), content_type="image/png"
        )

    def test_randomise_avatar_without_profile_picture(self):
        response = self.client.get(reverse("randomise_avatar"))

        self.user.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user.avatar_type, "random")
        self.assertIsNotNone(self.user.avatar_seed)
        self.assertFalse(self.user.profile_picture)

    def test_randomise_avatar_with_profile_picture_non_ai(self):
        self.user.profile_picture = self.create_test_image()
        self.user.avatar_type = "initials"
        self.user.save()

        response = self.client.get(reverse("randomise_avatar"))

        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user.avatar_type, "random")
        self.assertFalse(self.user.profile_picture)

    def test_randomise_avatar_with_profile_picture_ai_type(self):
        self.user.profile_picture = self.create_test_image()
        self.user.avatar_type = "ai"
        self.user.save()

        response = self.client.get(reverse("randomise_avatar"))

        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user.avatar_type, "random")
        self.assertTrue(self.user.profile_picture)

    def test_use_initials_avatar_without_profile_picture(self):
        """Test using initials when user has no profile picture."""
        self.user.avatar_type = "random"
        self.user.avatar_seed = "some-seed"
        self.user.save()

        response = self.client.get(reverse("use_initials_avatar"))

        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user.avatar_type, "initials")
        self.assertEqual(self.user.avatar_seed, "")

    def test_use_initials_avatar_with_profile_picture(self):
        """Test using initials when user has profile picture."""
        self.user.profile_picture = self.create_test_image()
        self.user.avatar_type = "random"
        self.user.save()

        response = self.client.get(reverse("use_initials_avatar"))

        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user.avatar_type, "initials")
        self.assertFalse(self.user.profile_picture)
        self.assertEqual(self.user.avatar_seed, "")

    def test_randomise_avatar_redirects_to_profile(self):
        """Test that randomise_avatar redirects to profile page."""
        response = self.client.get(reverse("randomise_avatar"))
        self.assertRedirects(response, reverse("profile"))

    def test_use_initials_avatar_redirects_to_profile(self):
        """Test that use_initials_avatar redirects to profile page."""
        response = self.client.get(reverse("use_initials_avatar"))
        self.assertRedirects(response, reverse("profile"))

    def test_randomise_avatar_shows_success_message(self):
        """Test that randomise_avatar shows success message."""
        response = self.client.get(reverse("randomise_avatar"), follow=True)
        messages = list(response.context["messages"])

        self.assertTrue(any("Avatar randomised" in str(m) for m in messages))

    def test_use_initials_avatar_shows_success_message(self):
        """Test that use_initials_avatar shows success message."""
        response = self.client.get(reverse("use_initials_avatar"), follow=True)
        messages = list(response.context["messages"])

        self.assertTrue(any("Avatar reset to initials" in str(m) for m in messages))

    def tearDown(self):
        if self.user.profile_picture:
            self.user.profile_picture.delete()
