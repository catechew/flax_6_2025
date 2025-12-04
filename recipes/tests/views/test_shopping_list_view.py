"""
Tests for ShoppingListView.
"""
from datetime import date
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipes.models.meal_plan import MealPlan
from recipes.models.recipe import Recipe
from recipes.helpers.meal_plan_helpers import create_meal_slots

User = get_user_model()


class ShoppingListViewTests(TestCase):
  """ 
  Tests for generating a shopping list from a meal plan. 
  """

  def setUp(self):
    self.user = User.objects.create_user(
      username="@shopuser",
      email="shop@example.com",
      password="Password123",
    )
    self.client.login(username="@shopuser", password="Password123")
    self.plan = MealPlan.objects.create(
      user=self.user,
      week_start=date(2025, 11, 24),
    )
    create_meal_slots(self.plan)
    self.recipe = Recipe.objects.create(
      title="Simple Meal",
      author=self.user,
      publication_date=date.today(),
      ingredients="Salt\nRice",
      steps="Cook",
    )

    slot = self.plan.entries.filter(meal_type="dinner").first()
    slot.recipe = self.recipe
    slot.save()

  def test_logged_in_user_can_view_shopping_list(self):
    url = reverse(
      "shopping-list",
      args=[self.plan.id],
    )

    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)

  def test_shopping_list_contains_ingredients(self):
    url = reverse(
      "shopping-list",
      args=[self.plan.id],
    )

    response = self.client.get(url)
    content = response.content.decode()

    self.assertIn("Salt", content)
    self.assertIn("Rice", content)

  def test_login_required(self):
    self.client.logout()

    url = reverse(
      "shopping-list",
      args=[self.plan.id],
    )

    response = self.client.get(url)
    self.assertEqual(response.status_code, 302)