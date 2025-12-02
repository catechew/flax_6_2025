"""
Tests for MealPlanNavigateView.
"""

from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from recipes.models.meal_plan import MealPlan
from recipes.helpers.meal_plan_helpers import create_meal_slots
from recipes.views.meal_plan_view import MealPlanNavigateView

User = get_user_model()


class MealPlanNavigateViewTests(TestCase):
    """ Tests for navigating between meal plans. """

    def setUp(self):
        self.user = User.objects.create_user(
            username="@navuser",
            email="nav@example.com",
            password="Password123",
        )
        self.client.login(username="@navuser", password="Password123")

        self.start_week = date(2025, 11, 24)
        self.plan = MealPlan.objects.create(
            user=self.user,
            week_start=self.start_week,
        )
        create_meal_slots(self.plan)

    def test_navigate_next_week_creates_new_plan(self):
        url = reverse("meal-plan-navigate", args=[self.plan.id, "next"])
        self.client.get(url)

        self.assertEqual(MealPlan.objects.count(), 2)

    def test_navigate_previous_week_creates_new_plan(self):
        url = reverse("meal-plan-navigate", args=[self.plan.id, "prev"])
        self.client.get(url)

        self.assertEqual(MealPlan.objects.count(), 2)

    def test_navigate_redirects_to_new_plan(self):
        url = reverse("meal-plan-navigate", args=[self.plan.id, "next"])
        response = self.client.get(url)

        new_plan = MealPlan.objects.exclude(id=self.plan.id).first()
        self.assertRedirects(
            response,
            reverse("meal-plan-detail", args=[new_plan.id]),
        )

    def test_invalid_direction_redirects_to_same_plan(self):
        url = reverse("meal-plan-navigate", args=[self.plan.id, "invalid"])
        response = self.client.get(url)

        self.assertRedirects(
            response,
            reverse("meal-plan-detail", args=[self.plan.id]),
        )

    def test_calculate_new_week_invalid_direction_returns_none(self):
        view = MealPlanNavigateView()

        result = view._calculate_new_week(self.plan, "invalid")
        self.assertIsNone(result)

    def test_login_required(self):
        self.client.logout()

        url = reverse("meal-plan-navigate", args=[self.plan.id, "next"])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        
    def test_navigate_next_week_existing_plan_does_not_create_new_one(self):
        """
        Covers created=False branch.
        """

        # First navigation → creates next week plan
        url = reverse("meal-plan-navigate", args=[self.plan.id, "next"])
        self.client.get(url)

        # Second navigation → same next week already exists
        self.client.get(url)

        # Still only 2 plans total
        self.assertEqual(MealPlan.objects.count(), 2)
