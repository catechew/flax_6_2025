from datetime import date
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipes.models.meal_plan import MealPlan, MealSlot
from recipes.models.recipe import Recipe
from recipes.helpers.meal_plan_helpers import create_meal_slots

"""
Tests for MealSlotUpdateView.
"""

User = get_user_model()


class MealSlotUpdateViewTests(TestCase):
 """ 
 Tests for updating a meal slot with a recipe. 
 """

 def setUp(self):
  self.user = User.objects.create_user(
   username="@slotupdate",
   email="slotupdate@example.com",
   password="Password123",
  )
  self.client.login(username="@slotupdate", password="Password123")

  self.plan = MealPlan.objects.create(
   user=self.user,
   week_start=date(2025, 11, 24),
  )
  create_meal_slots(self.plan)

  self.slot = self.plan.entries.first()

  self.recipe = Recipe.objects.create(
   title="Test Recipe",
   author=self.user,
   publication_date=date.today(),
   ingredients="Salt\nPepper",
   steps="Cook",
  )

 def test_get_update_page_returns_200(self):
  url = reverse("meal-slot-update", args=[self.slot.id])
  response = self.client.get(url)
  self.assertEqual(response.status_code, 200)

 def test_post_updates_slot_recipe(self):
  url = reverse("meal-slot-update", args=[self.slot.id])
  self.client.post(url, {"recipe_id": self.recipe.id})

  self.slot.refresh_from_db()
  self.assertEqual(self.slot.recipe, self.recipe)

 def test_post_with_no_recipe_id_clears_slot(self):
  url = reverse("meal-slot-update", args=[self.slot.id])
  self.client.post(url, {})

  self.slot.refresh_from_db()
  self.assertIsNone(self.slot.recipe)

 def test_login_required(self):
  self.client.logout()
  url = reverse("meal-slot-update", args=[self.slot.id])
  response = self.client.get(url)
  self.assertEqual(response.status_code, 302)

  def test_post_with_no_recipe_does_not_crash(self):
    url = reverse("meal-slot-update", args=[self.slot.id])
    self.client.post(url, {})
    self.slot.refresh_from_db()
    self.assertIsNone(self.slot.recipe)