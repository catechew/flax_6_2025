"""
Tests for shopping list helper functions.
"""

from collections import defaultdict
from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase

from recipes.helpers.shopping_list_helpers import (
 categorise_ingredient,
 extract_ingredients,
 consolidate_ingredients,
 organise_shopping_list,
)
from recipes.models.meal_plan import MealPlan, MealSlot
from recipes.models.recipe import Recipe

User = get_user_model()


class CategoriseIngredientTests(TestCase):
 """ Tests for categorise_ingredient helper. """

 def test_known_meat_category(self):
  category = categorise_ingredient("Chicken breast")

  self.assertEqual(category, "🥩 Meat & Poultry")

 def test_unknown_ingredient_returns_other(self):
  category = categorise_ingredient("Protein powder")

  self.assertEqual(category, "🛒 Other Items")


class ExtractIngredientsTests(TestCase):
 """ Tests for extract_ingredients helper. """

 def setUp(self):
  self.user = User.objects.create_user(
   username="@shopuser",
   email="shop@example.com",
   password="Password123",
  )
  self.plan = MealPlan.objects.create(
   user=self.user,
   week_start=date(2025, 11, 24),
  )
  self.recipe = Recipe.objects.create(
   title="Test Meal",
   author=self.user,
   publication_date=date.today(),
   ingredients="Chicken\nRice",
   steps="Cook",
  )
  self.slot = MealSlot.objects.create(
   meal_plan=self.plan,
   day="mon",
   meal_type="dinner",
   recipe=self.recipe,
  )

 def test_extracts_ingredients_by_category(self):
  slots = self.plan.entries.all()
  shopping_list = extract_ingredients(slots)

  self.assertIsInstance(shopping_list, defaultdict)
  self.assertIn("🥩 Meat & Poultry", shopping_list)
  self.assertIn("🌾 Grains & Pasta", shopping_list)

 def test_empty_ingredient_lines_are_ignored(self):
  recipe = Recipe.objects.create(
   title="Empty Lines",
   author=self.user,
   publication_date=date.today(),
   ingredients="\n  \nSalt\n",
   steps="Cook",
  )

  MealSlot.objects.create(
   meal_plan=self.plan,
   day="tue",
   meal_type="dinner",
   recipe=recipe,
  )

  shopping_list = extract_ingredients(self.plan.entries.all())

  self.assertEqual(len(shopping_list["🧂 Condiments"]), 1)


class ConsolidateIngredientsTests(TestCase):
 """ Tests for consolidate_ingredients helper. """

 def test_duplicate_items_are_grouped(self):
  items = [
   {"item": "Rice", "recipe": "R1", "day": "Mon", "meal": "Dinner"},
   {"item": "Rice", "recipe": "R2", "day": "Tue", "meal": "Lunch"},
  ]

  consolidated = consolidate_ingredients(items)

  self.assertEqual(len(consolidated), 1)
  self.assertEqual(consolidated[0]["count"], 2)


class OrganiseShoppingListTests(TestCase):
 """ Tests for organise_shopping_list helper. """

 def test_orders_categories_correctly(self):
  shopping_list = {
   "🛒 Other Items": [{"item": "Protein"}],
   "🥬 Vegetables": [{"item": "Spinach"}],
  }

  organised = organise_shopping_list(shopping_list)

  self.assertEqual(organised[0][0], "🥬 Vegetables")
  self.assertEqual(organised[1][0], "🛒 Other Items")