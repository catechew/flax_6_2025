from datetime import date
from django.test import TestCase
from django.contrib.auth import get_user_model

from recipes.models.meal_plan import MealPlan, MealSlot
from recipes.models.recipe import Recipe
from recipes.helpers.meal_plan_helpers import (
    get_monday,
    calculate_completion,
    create_meal_slots,
    reuse_prev_week,
    calculate_meals_logged,
)

User = get_user_model()

"""
Tests for meal plan helper functions.
"""

class GetMondayHelperTests(TestCase):
    """ 
    Tests for get_monday helper. 
    """

    def test_returns_monday_for_midweek_date(self):
        test_date = date(2025, 11, 27)
        self.assertEqual(get_monday(test_date), date(2025, 11, 24))

    def test_returns_same_date_if_monday(self):
        test_date = date(2025, 11, 24)
        self.assertEqual(get_monday(test_date), test_date)


class CalculateCompletionHelperTests(TestCase):
    """
    Tests for calculate_completion helper.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="@helperuser",
            email="helper@example.com",
            password="Password123",
        )
        self.plan = MealPlan.objects.create(
            user=self.user,
            week_start=date(2025, 11, 24),
        )
        self.recipe = Recipe.objects.create(
            title="Helper Test Recipe",
            author=self.user,
            publication_date=date(2025, 11, 24),
            ingredients="Salt\nPepper",
            steps="Cook",
        )

    def test_returns_zero_when_no_slots_exist(self):
        self.assertEqual(calculate_completion(self.plan), 0)

    def test_returns_zero_when_slots_have_no_recipes(self):
        MealSlot.objects.create(
            meal_plan=self.plan,
            day="mon",
            meal_type="breakfast",
        )
        self.assertEqual(calculate_completion(self.plan), 0)

    def test_returns_full_completion_when_all_meals_filled(self):
        for meal in ("breakfast", "lunch", "dinner"):
            MealSlot.objects.create(
                meal_plan=self.plan,
                day="mon",
                meal_type=meal,
                recipe=self.recipe,
            )
        self.assertEqual(calculate_completion(self.plan), 100)


class CreateMealSlotsHelperTests(TestCase):
    """ 
    Tests for create_meal_slots helper. 
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="@slotuser",
            email="slot@example.com",
            password="Password123",
        )
        self.plan = MealPlan.objects.create(
            user=self.user,
            week_start=date(2025, 11, 24),
        )

    def test_creates_expected_number_of_meal_slots(self):
        create_meal_slots(self.plan)
        self.assertEqual(self.plan.entries.count(), 28)

    def test_raises_error_when_called_twice(self):
        create_meal_slots(self.plan)
        with self.assertRaises(Exception):
            create_meal_slots(self.plan)


class ReusePrevWeekHelperTests(TestCase):
    """
    Tests for reuse_prev_week helper.  
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="@reuseuser",
            password="Password123",
        )
        self.previous_plan = MealPlan.objects.create(
            user=self.user,
            week_start=date(2025, 11, 17),
        )
        self.current_plan = MealPlan.objects.create(
            user=self.user,
            week_start=date(2025, 11, 24),
        )

        create_meal_slots(self.previous_plan)
        create_meal_slots(self.current_plan)

    def test_copies_meals_from_previous_week(self):
        previous_slot = self.previous_plan.entries.filter(
            day="mon",
            meal_type="breakfast",
        ).first()
        previous_slot.notes = "Test notes"
        previous_slot.save()

        result = reuse_prev_week(self.current_plan)
        self.assertTrue(result)

        new_slot = self.current_plan.entries.filter(
            day="mon",
            meal_type="breakfast",
        ).first()
        self.assertEqual(new_slot.notes, "Test notes")

    def test_returns_false_when_no_previous_plan_exists(self):
        new_plan = MealPlan.objects.create(
            user=self.user,
            week_start=date(2026, 1, 1),  
        )
        self.assertFalse(reuse_prev_week(new_plan))
