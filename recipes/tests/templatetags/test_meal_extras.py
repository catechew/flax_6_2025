"""
Tests for meal_extras template filters.
"""

from django.test import SimpleTestCase

from recipes.templatetags.meal_extras import ordinal
from recipes.templatetags.meal_plan_filters import get_item, get_slot

class OrdinalFilterTests(SimpleTestCase):
 """ Tests for ordinal template filter. """

 def test_string_special_cases(self):
    self.assertEqual(ordinal("11"), "11th")
    self.assertEqual(ordinal("12"), "12th")
    self.assertEqual(ordinal("13"), "13th")

 def test_large_number_suffixes(self):
    self.assertEqual(ordinal(112), "112th")
    self.assertEqual(ordinal(213), "213th")

 def test_standard_suffixes(self):
  self.assertEqual(ordinal(1), "1st")
  self.assertEqual(ordinal(2), "2nd")
  self.assertEqual(ordinal(3), "3rd")

 def test_default_th_suffix(self):
  self.assertEqual(ordinal(4), "4th")
  self.assertEqual(ordinal(10), "10th")

 def test_string_input_is_converted(self):
  self.assertEqual(ordinal("21"), "21st")
  

class GetItemFilterTests(SimpleTestCase):
    def test_returns_value_for_valid_key(self):
        data = {"a": 1, "b": 2}
        self.assertEqual(get_item(data, "a"), 1)

    def test_returns_none_for_invalid_dict(self):
        self.assertIsNone(get_item(None, "a"))

    def test_returns_none_for_missing_key(self):
        data = {"a": 1}
        self.assertIsNone(get_item(data, "b"))  


class GetSlotFilterTests(SimpleTestCase):
    def test_returns_value_for_valid_meal(self):
        day = {"breakfast": "Eggs", "dinner": "Pasta"}
        self.assertEqual(get_slot(day, "dinner"), "Pasta")

    def test_returns_none_for_invalid_dict(self):
        self.assertIsNone(get_slot(None, "lunch"))

    def test_returns_none_for_missing_meal_type(self):
        day = {"breakfast": "Eggs"}
        self.assertIsNone(get_slot(day, "dinner"))  