""" 
Recipe tag and adjective tests.
"""
from django.test import TestCase
from recipes.tests.utils import create_test_user, create_test_recipe

class RecipeModelTagTests(TestCase):
    def setUp(self):
        self.recipe = create_test_recipe(author=create_test_user())

    def test_tag_lists_return_values(self):
        self.recipe.course_tags = "breakfast,main"
        self.recipe.save()
        self.assertEqual(len(self.recipe.get_course_tags_list()), 2)

    def test_all_tags_combined(self):
        self.recipe.course_tags = "breakfast"
        self.recipe.dietary_tags = "vegan"
        self.recipe.save()
        tags = self.recipe.get_all_tags_list()
        self.assertIn("breakfast", tags)
        self.assertIn("vegan", tags)

    def test_empty_tags_produce_none_adjectives(self):
        self.recipe.course_tags = ""
        self.recipe.save()
        self.assertEqual(self.recipe.adjectives, "none")
