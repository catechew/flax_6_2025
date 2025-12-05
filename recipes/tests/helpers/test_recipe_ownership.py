from django.test import TestCase
from unittest.mock import MagicMock
from recipes.helpers.recipe_ownership import (
    determine_ownership,
    prepare_recipe_author,
)


class DetermineOwnershipTests(TestCase):

    def test_returns_true_when_missing(self):
        self.assertTrue(determine_ownership({}))

    def test_returns_false_when_set(self):
        self.assertFalse(determine_ownership({"is_owner": False}))


class PrepareRecipeAuthorTests(TestCase):

    def test_non_owner_copy_clears_ids(self):
        recipe = MagicMock(pk=5, id=5)
        user = MagicMock()
        original = MagicMock()

        prepare_recipe_author(recipe, user, original, False)

        self.assertIsNone(recipe.pk)
        self.assertIsNone(recipe.id)
        self.assertEqual(recipe.author, user)

    def test_owner_update_does_not_reset_ids(self):
        recipe = MagicMock(pk=5, id=5)
        user = MagicMock()
        original = MagicMock()

        prepare_recipe_author(recipe, user, original, True)

        self.assertEqual(recipe.pk, 5)
        self.assertEqual(recipe.id, 5)

    def test_create_mode_sets_author(self):
        recipe = MagicMock()
        user = MagicMock()

        prepare_recipe_author(recipe, user, None, True)

        self.assertEqual(recipe.author, user)
