"""
Tests for MealSlot model.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from datetime import date
from recipes.models.meal_plan import MealPlan, MealSlot
from recipes.models.recipe import Recipe

User = get_user_model()


class MealSlotModelTest(TestCase):
    """
    Test MealSlot behaviour.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="@slotuser", password="Password123"
        )
        self.plan = MealPlan.objects.create(
            user=self.user, week_start=date(2025, 11, 24)
        )
        self.recipe = Recipe.objects.create(
            title="Test Recipe",
            author=self.user,
            publication_date=date.today(),
            ingredients="Salt (1 tsp)",
            steps="Cook",
        )

    def test_slot_creation_without_recipe(self):
        slot = MealSlot.objects.create(
            meal_plan=self.plan, day="mon", meal_type="breakfast"
        )
        self.assertIsNone(slot.recipe)

    def test_slot_with_recipe(self):
        slot = MealSlot.objects.create(
            meal_plan=self.plan, day="tue", meal_type="lunch", recipe=self.recipe
        )
        self.assertEqual(slot.recipe, self.recipe)

    def test_unique_day_meal_constraint(self):
        MealSlot.objects.create(meal_plan=self.plan, day="wed", meal_type="dinner")
        with self.assertRaises(IntegrityError):
            MealSlot.objects.create(meal_plan=self.plan, day="wed", meal_type="dinner")

    def test_same_day_different_meals_allowed(self):
        slot1 = MealSlot.objects.create(
            meal_plan=self.plan, day="thu", meal_type="breakfast"
        )
        slot2 = MealSlot.objects.create(
            meal_plan=self.plan, day="thu", meal_type="lunch"
        )
        self.assertNotEqual(slot1.id, slot2.id)

    def test_string_representation(self):
        slot = MealSlot.objects.create(
            meal_plan=self.plan, day="mon", meal_type="dinner"
        )
        self.assertEqual(str(slot), "Monday - Dinner")

    def test_recipe_deleted_sets_null(self):
        slot = MealSlot.objects.create(
            meal_plan=self.plan, day="fri", meal_type="lunch", recipe=self.recipe
        )
        self.recipe.delete()
        slot.refresh_from_db()
        self.assertIsNone(slot.recipe)

    def test_meal_slot_related_name(self):
        MealSlot.objects.create(meal_plan=self.plan, day="sat", meal_type="dinner")
        self.assertEqual(self.plan.entries.count(), 1)
