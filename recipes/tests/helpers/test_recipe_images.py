from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from recipes.helpers.recipe_images import (
    copy_original_image,
    delete_image_if_requested
)
from recipes.tests.utils import create_test_recipe, create_test_image


class RecipeImageHelpersTestCase(TestCase):
    """
    Tests for recipe image helper functions.
    """

    def test_copy_original_image_success(self):
        """ Test copying image from original recipe to new recipe. """
        image = create_test_image()
        original = create_test_recipe()
        original.image = image
        original.save()
        new_recipe = create_test_recipe(title="Modified Recipe")
        copy_original_image(new_recipe, original)
        self.assertTrue(new_recipe.image)
        self.assertIn('test', new_recipe.image.name)

    def test_copy_original_image_no_original_recipe(self):
        """ Test copy when original_recipe is None. """
        recipe = create_test_recipe()
        copy_original_image(recipe, None)
        self.assertFalse(recipe.image)

    def test_copy_original_image_no_original_image(self):
        """ Test copy when original recipe has no image. """
        original = create_test_recipe()
        new_recipe = create_test_recipe(title="New Recipe")

        copy_original_image(new_recipe, original)
        self.assertFalse(new_recipe.image)

    def test_copy_original_image_recipe_already_has_image(self):
        """ Test copy when new recipe already has an image. """
        image1 = create_test_image(name='original.jpg')
        original = create_test_recipe()
        original.image = image1
        original.save()

        image2 = create_test_image(name='new.jpg')
        new_recipe = create_test_recipe(title="New Recipe")
        new_recipe.image = image2
        new_recipe.save()
        original_image_name = new_recipe.image.name

        copy_original_image(new_recipe, original)
        self.assertEqual(new_recipe.image.name, original_image_name)

    def test_delete_image_if_requested_success(self):
        """ Test deleting image when owner requests it. """
        image = create_test_image()
        original = create_test_recipe()
        original.image = image
        original.save()

        recipe = create_test_recipe(title="Modified Recipe")
        recipe.image = create_test_image(name='recipe.jpg')
        recipe.save()
        session_data = {"image_clear": True}

        delete_image_if_requested(recipe, session_data, original, is_owner=True)

        self.assertFalse(recipe.image.name)

    def test_delete_image_no_original_recipe(self):
        recipe = create_test_recipe()
        recipe.image = create_test_image()
        recipe.save()
        session_data = {"image_clear": True}

        delete_image_if_requested(recipe, session_data, None, is_owner=True)
        self.assertIsNotNone(recipe.image)

    def test_delete_image_not_owner(self):
        original = create_test_recipe()
        recipe = create_test_recipe(title="Modified")
        recipe.image = create_test_image()
        recipe.save()
        session_data = {"image_clear": True}

        delete_image_if_requested(recipe, session_data, original, is_owner=False)
        self.assertIsNotNone(recipe.image)

    def test_delete_image_no_clear_flag(self):
        """Test delete when image_clear flag is not set"""
        original = create_test_recipe()
        recipe = create_test_recipe(title="Modified")
        recipe.image = create_test_image()
        recipe.save()

        session_data = {}

        delete_image_if_requested(recipe, session_data, original, is_owner=True)
        self.assertIsNotNone(recipe.image)

    def test_delete_image_no_image_to_delete(self):
        original = create_test_recipe()
        recipe = create_test_recipe(title="Modified")

        session_data = {"image_clear": True}

        delete_image_if_requested(recipe, session_data, original, is_owner=True)
        self.assertFalse(recipe.image)