"""
Tests for meal_plan_filters template filters.
Forces module import so coverage tracks execution.
"""

from django.test import SimpleTestCase

# ✅ CRUCIAL: import the module itself
import recipes.templatetags.meal_plan_filters as filters


class MealPlanFiltersTests(SimpleTestCase):
    """Tests for meal plan template filters."""

    def test_get_item_valid_dict(self):
        self.assertEqual(filters.get_item({"a": 1}, "a"), 1)

    def test_get_item_missing_key(self):
        self.assertIsNone(filters.get_item({"a": 1}, "b"))

    def test_get_item_non_dict(self):
        self.assertIsNone(filters.get_item("not-a-dict", "a"))

    def test_get_slot_valid_dict(self):
        self.assertEqual(
            filters.get_slot({"breakfast": "Eggs"}, "breakfast"),
            "Eggs"
        )

    def test_get_slot_missing_key(self):
        self.assertIsNone(
            filters.get_slot({"breakfast": "Eggs"}, "dinner")
        )

    def test_get_slot_non_dict(self):
        self.assertIsNone(filters.get_slot(None, "lunch"))
