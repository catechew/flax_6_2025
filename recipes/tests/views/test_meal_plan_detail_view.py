"""
Tests for meal plan detail view.
"""
from datetime import date
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipes.models.meal_plan import MealPlan
from recipes.models.recipe import Recipe
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
    Tests for MealPlanReuseLastWeekView.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="@reuseuser",
            email="reuse@example.com",
            password="Password123"
        )
        self.client.login(username="@reuseuser", password="Password123")
        
        # Create a recipe
        self.recipe = Recipe.objects.create(
            title='Test Recipe',
            author=self.user,
            publication_date=timezone.now().date(),
            servings=4,
            ingredients='Test (1)',
            steps='Test steps',
            prep_time_hours=0,
            prep_time_minutes=30,
            cook_time_hours=1,
            cook_time_minutes=15
        )
        
        # Create current week's plan
        self.current_plan = MealPlan.objects.create(
            user=self.user,
            week_start=date(2025, 12, 1)
        )
        create_meal_slots(self.current_plan)
        
        # Create previous week's plan
        self.prev_plan = MealPlan.objects.create(
            user=self.user,
            week_start=date(2025, 11, 24)
        )
        create_meal_slots(self.prev_plan)
        
        self.url = reverse("meal-plan-reuse-last-week", args=[self.current_plan.id])

    def test_reuse_last_week_no_previous_meals_shows_warning(self):
        response = self.client.post(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertTrue(any('No meals from last week' in str(m) for m in messages))

    def test_reuse_last_week_with_previous_meals_success(self):
        """Test when previous week has meals (FALSE branch - LINE 215)."""
        # Assign recipe to breakfast/lunch/dinner slots
        for slot in self.prev_plan.entries.filter(meal_type__in=['breakfast', 'lunch', 'dinner']):
            slot.recipe = self.recipe
            slot.save()
        
        # Call reuse
        response = self.client.post(self.url)
        
        # Just verify it redirects properly
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("meal-plan-detail", args=[self.current_plan.id]))
    
    def test_reuse_redirects_to_plan_detail(self):
        """ Test that reuse redirects to meal plan detail page. """
        response = self.client.post(self.url)
        self.assertRedirects(
            response,
            reverse("meal-plan-detail", args=[self.current_plan.id])
        )

    def test_login_required(self):
        """ Test that login is required. """
        self.client.logout()
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/log_in/', response.url)
