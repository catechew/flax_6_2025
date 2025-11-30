"""
Tests for meal_extras template filters.
"""

from django.test import SimpleTestCase

from recipes.templatetags.meal_extras import ordinal


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