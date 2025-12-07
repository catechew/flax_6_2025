from datetime import date
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from recipes.models.meal_plan import MealPlan

User = get_user_model()


class MealPlanModelTests(TestCase):
  """
  Tests for the MealPlan model including creation, constraints and display.
  """
  
  def setUp(self):
    """Create a base user and week_start date used in multiple tests."""
    self.user = User.objects.create_user(
        username="@mealuser",
        password="Password123",
    )
    self.week_start = date(2025, 11, 24)
        
  def test_meal_plan_can_be_created(self):
      """MealPlan instance can be successfully created for a user."""
      plan = MealPlan.objects.create(
          user=self.user,
          week_start=self.week_start,
      )
      self.assertEqual(plan.user, self.user)
      self.assertEqual(plan.week_start, self.week_start)

  def test_user_cannot_have_two_plans_for_same_week(self):
      """A user cannot create two plans for the same week (unique_together)."""
      MealPlan.objects.create(
          user=self.user,
          week_start=self.week_start,
      )

      with self.assertRaises(IntegrityError):
          MealPlan.objects.create(
              user=self.user,
              week_start=self.week_start,
          )

  def test_same_week_allowed_for_different_users(self):
      """Different users may create meal plans for the same week."""
      other_user = User.objects.create_user(
          username="@otheruser",
          password="Password123",
      )

      plan_one = MealPlan.objects.create(
          user=self.user,
          week_start=self.week_start,
      )
      plan_two = MealPlan.objects.create(
          user=other_user,
          week_start=self.week_start,
      )

      self.assertNotEqual(plan_one.user, plan_two.user)

  def test_string_representation_is_readable(self):
      """Test that __str__ returns a clear, readable description."""
      plan = MealPlan.objects.create(
          user=self.user,
          week_start=self.week_start,
      )

      expected = "@mealuser's plan for 2025-11-24"
      self.assertEqual(str(plan), expected)