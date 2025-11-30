"""
Tests for MealSlotNotesView.
"""

from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from recipes.models.meal_plan import MealPlan
from recipes.helpers.meal_plan_helpers import create_meal_slots

User = get_user_model()


class MealSlotNotesViewTests(TestCase):
  """ Tests for adding and updating meal slot notes. """

  def setUp(self):
    self.user = User.objects.create_user(
      username="@notesuser",
      email="notes@example.com",
      password="Password123",
    )
    self.client.login(username="@notesuser", password="Password123")

    self.plan = MealPlan.objects.create(
      user=self.user,
      week_start=date(2025, 11, 24),
    )
    create_meal_slots(self.plan)

    self.slot = self.plan.entries.filter(meal_type="snack").first()

  def test_post_saves_notes_to_slot(self):
    url = reverse(
      "meal-slot-notes",
      args=[self.slot.id],
    )

    self.client.post(
      url,
      {"notes": "Protein shake and banana"},
    )

    self.slot.refresh_from_db()
    self.assertEqual(self.slot.notes, "Protein shake and banana")

  def test_redirects_to_meal_plan_detail(self):
    url = reverse(
      "meal-slot-notes",
      args=[self.slot.id],
    )

    response = self.client.post(
      url,
      {"notes": "Yoghurt"},
    )

    self.assertRedirects(
      response,
      reverse("meal-plan-detail", args=[self.plan.id]),
    )

  def test_login_required(self):
    self.client.logout()

    url = reverse(
      "meal-slot-notes",
      args=[self.slot.id],
    )

    response = self.client.post(
      url,
      {"notes": "Should not save"},
    )

    self.assertEqual(response.status_code, 302)
