"""
Tests for the meal plan creation view.
"""

from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from recipes.models.meal_plan import MealPlan

User = get_user_model()


class MealPlanCreateViewTests(TestCase):
  """ Tests for MealPlanCreateView. """

  def setUp(self):
    self.user = User.objects.create_user(
      username="@createuser",
      email="create@example.com",
      password="Password123",
    )
    self.url = reverse("meal-plan-create")

  def test_login_required(self):
    response = self.client.get(self.url)

    self.assertEqual(response.status_code, 302)

  def test_creates_meal_plan_on_get(self):
    self.client.login(
      username="@createuser",
      password="Password123",
    )

    response = self.client.get(self.url)

    self.assertEqual(response.status_code, 302)
    self.assertEqual(MealPlan.objects.count(), 1)
