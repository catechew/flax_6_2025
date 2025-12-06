"""
Tests for meal plan detail view.
"""
from datetime import date
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipes.models.meal_plan import MealPlan
from recipes.helpers.meal_plan_helpers import create_meal_slots

User = get_user_model()


class MealPlanDetailViewTests(TestCase):
    """ 
    Tests for MealPlanDetailView. 
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="@detailuser",
            email="detail@example.com",
            password="Password123",
        )

        self.plan = MealPlan.objects.create(
            user=self.user,
            week_start=date(2025, 11, 24),
        )

        create_meal_slots(self.plan)

        self.url = reverse(
            "meal-plan-detail",
            args=[self.plan.id],
        )

    def test_login_required(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_logged_in_user_can_view_plan(self):
        self.client.login(
            username="@detailuser",
            password="Password123",
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class MealPlanReuseLastWeekViewTests(TestCase):
    """ 
    Tests for reusing last week's meal plan. 
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="@reuseuser",
            password="Password123"
        )

        self.plan = MealPlan.objects.create(
            user=self.user,
            week_start=date(2025, 11, 24)
        )

        create_meal_slots(self.plan)

        self.url = reverse(
            "meal-plan-reuse-last-week",
            args=[self.plan.id],
        )

        self.client.login(
            username="@reuseuser",
            password="Password123"
        )

    def test_reuse_last_week_button_post(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        
    def test_reuse_last_week_with_previous_plan(self):
        # Create previous week's plan
        prev_plan = MealPlan.objects.create(
            user=self.user,
            week_start=date(2025, 11, 17),
        )

        create_meal_slots(prev_plan)

        # Add some data to previous plan
        slot = prev_plan.entries.first()
        slot.notes = "Copied note"
        slot.save()

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 302)

        # Confirm notes were copied
        new_slot = self.plan.entries.first()
        self.assertEqual(new_slot.notes, "Copied note")
    
    def test_reuse_last_week_shows_warning_when_none_available(self):
        # Ensure no previous plan exists
        MealPlan.objects.filter(
            user=self.user,
            week_start=date(2025, 11, 17)
        ).delete()

        response = self.client.post(self.url, follow=True)

        messages = list(response.context['messages'])

        self.assertTrue(any(
            "No meals from last week available to reuse." in str(m)
            for m in messages
        ))