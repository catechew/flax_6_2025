"""
Tests for MealSlotClearView.
"""
from datetime import date
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipes.models.meal_plan import MealPlan
from recipes.models.recipe import Recipe
from recipes.helpers.meal_plan_helpers import create_meal_slots

User = get_user_model()


class MealSlotClearViewTests(TestCase):
  """ 
  Tests for clearing a meal slot.
  """

  def setUp(self):
    self.user = User.objects.create_user(
      username="@clearslot",
      email="clear@example.com",
      password="Password123",
    )
    self.client.login(username="@clearslot", password="Password123")
    self.plan = MealPlan.objects.create(
      user=self.user,
      week_start=date(2025, 11, 24),
    )
    create_meal_slots(self.plan)
    self.slot = self.plan.entries.first()
    self.recipe = Recipe.objects.create(
      title="Clear Me",
      author=self.user,
      publication_date=date.today(),
      ingredients="Water",
      steps="Boil",
    )
    self.slot.recipe = self.recipe
    self.slot.save()

  def test_clears_recipe_from_slot(self):
    url = reverse(
      "meal-slot-clear",
      args=[self.slot.id],
    )
    self.client.get(url)

    self.slot.refresh_from_db()
    self.assertIsNone(self.slot.recipe)

  def test_redirects_to_meal_plan_detail(self):
    url = reverse(
      "meal-slot-clear",
      args=[self.slot.id],
    )
    response = self.client.get(url)
    self.assertRedirects(
      response,
      reverse("meal-plan-detail", args=[self.plan.id]),
    )

  def test_login_required(self):
    self.client.logout()
    url = reverse(
      "meal-slot-clear",
      args=[self.slot.id],
    )
    response = self.client.get(url)
    self.assertEqual(response.status_code, 302)