"""
Tests for meal_plan_filters template filters.
"""

from django.test import SimpleTestCase

from recipes.templatetags.meal_plan_filters import get_item, get_slot


class GetItemFilterTests(SimpleTestCase):
 """ Tests for get_item filter. """

 def test_returns_value_for_valid_key(self):
  data = {"a": 1, "b": 2}

  self.assertEqual(get_item(data, "a"), 1)

 def test_returns_none_for_invalid_dict(self):
  self.assertIsNone(get_item(None, "a"))


class GetSlotFilterTests(SimpleTestCase):
 """ Tests for get_slot filter. """

 def test_returns_value_for_valid_meal(self):
  day = {"breakfast": "Eggs", "dinner": "Pasta"}

  self.assertEqual(get_slot(day, "dinner"), "Pasta")

 def test_returns_none_for_invalid_dict(self):
  self.assertIsNone(get_slot(None, "lunch"))
