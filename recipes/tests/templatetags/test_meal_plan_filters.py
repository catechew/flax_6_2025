"""
Tests for meal_plan_filters template filters.
"""

from django.test import TestCase
from recipes.templatetags.meal_plan_filters import get_item, get_slot


class MealPlanFiltersTests(TestCase):

    def test_get_item_returns_value_for_dict(self):
        data = {"a": 1}
        self.assertEqual(get_item(data, "a"), 1)

    def test_get_item_returns_none_for_non_dict(self):
        self.assertIsNone(get_item("not a dict", "a"))

    def test_get_slot_returns_value_for_dict(self):
        day = {"breakfast": "eggs"}
        self.assertEqual(get_slot(day, "breakfast"), "eggs")

    def test_get_slot_returns_none_for_non_dict(self):
        self.assertIsNone(get_slot("not a dict", "breakfast"))