from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage
from recipes.helpers.recipe_form_images import (
    _get_temp_file_prefix,
    save_temp_image,
    load_temp_image,
    cleanup_temp_image,
)

"""
Tests for recipe form image helper functions.
"""

class RecipeFormImagesTestCase(TestCase):
    """
    Test suite for recipe form image helper functions.
    """

    def tearDown(self):
        """ Clean up any temp files created during tests. """
        self._cleanup_all_temp_files()

    def _cleanup_all_temp_files(self):
        """Delete all files in temp directory."""
        try:
            temp_files = default_storage.listdir('temp')[1]
            self._delete_temp_files(temp_files)
        except Exception:
            pass

    def _delete_temp_files(self, file_list):
        """Delete each file in the given list."""
        for path in file_list:
            default_storage.delete(f'temp/{path}')

    def test_get_temp_file_prefix_without_recipe_id(self):
        """Test prefix generation without recipe_id."""
        prefix = _get_temp_file_prefix(user_id=123)
        self.assertEqual(prefix, "temp_123_")

    def test_get_temp_file_prefix_with_recipe_id(self):
        """Test prefix generation with recipe_id."""
        prefix = _get_temp_file_prefix(user_id=123, recipe_id=456)
        self.assertEqual(prefix, "temp_update_123_456_")

    def test_save_temp_image_with_none(self):
        """Test save_temp_image returns None when no file provided."""
        result = save_temp_image(None, user_id=123)
        self.assertIsNone(result)

    def test_save_temp_image_with_valid_file(self):
        """Test save_temp_image saves file and returns path."""
        uploaded_file = SimpleUploadedFile(
            "test_image.jpg",
            b"fake image content",
            content_type="image/jpeg"
        )

        result = save_temp_image(uploaded_file, user_id=123)

        self.assertIsNotNone(result)
        self.assertIn("temp/", result)
        self.assertIn("temp_123_", result)
        self.assertIn("test_image.jpg", result)
        self.assertTrue(default_storage.exists(result))
        default_storage.delete(result)

    def test_save_temp_image_with_recipe_id(self):
        """Test save_temp_image with recipe_id includes it in filename."""
        uploaded_file = SimpleUploadedFile(
            "update_image.jpg",
            b"fake image content",
            content_type="image/jpeg"
        )

        result = save_temp_image(uploaded_file, user_id=123, recipe_id=456)

        self.assertIsNotNone(result)
        self.assertIn("temp_update_123_456_", result)
        self.assertTrue(default_storage.exists(result))
        default_storage.delete(result)

    def test_load_temp_image_with_none_path(self):
        """Test load_temp_image returns empty dict when path is None."""
        result = load_temp_image(None, user_id=123)
        self.assertEqual(result, {})

    def test_load_temp_image_with_nonexistent_path(self):
        """Test load_temp_image returns empty dict when file doesn't exist."""
        result = load_temp_image("temp/nonexistent.jpg", user_id=123)
        self.assertEqual(result, {})

    def test_load_temp_image_with_existing_file(self):
        """Test load_temp_image returns SimpleUploadedFile dict."""
        uploaded_file = SimpleUploadedFile(
            "test_load.jpg",
            b"fake image content",
            content_type="image/jpeg"
        )
        temp_path = save_temp_image(uploaded_file, user_id=123)

        result = load_temp_image(temp_path, user_id=123)

        self.assertIn("image", result)
        self.assertIsInstance(result["image"], SimpleUploadedFile)
        self.assertEqual(result["image"].name, "test_load.jpg")
        self.assertEqual(result["image"].read(), b"fake image content")

        default_storage.delete(temp_path)

    def test_cleanup_temp_image_with_none(self):
        """Test cleanup_temp_image handles None gracefully."""
        cleanup_temp_image(None)

    def test_cleanup_temp_image_with_nonexistent_path(self):
        """Test cleanup_temp_image handles nonexistent file gracefully."""
        cleanup_temp_image("temp/nonexistent.jpg")

    def test_cleanup_temp_image_with_existing_file(self):
        """Test cleanup_temp_image deletes existing file."""
        uploaded_file = SimpleUploadedFile(
            "test_cleanup.jpg",
            b"fake image content",
            content_type="image/jpeg"
        )
        temp_path = save_temp_image(uploaded_file, user_id=123)
        self.assertTrue(default_storage.exists(temp_path))

        cleanup_temp_image(temp_path)

        self.assertFalse(default_storage.exists(temp_path))