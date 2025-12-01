""" Meal plan management views. """

from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from datetime import date, timedelta

from recipes.models.meal_plan import MealPlan, MealSlot
from recipes.models.recipe import Recipe
from recipes.helpers.meal_plan_helpers import (
    get_monday,
    calculate_completion,
    build_week_schedule,
    create_meal_slots,
    reuse_prev_week,
)
from recipes.helpers.shopping_list_helpers import (
    extract_ingredients, organise_shopping_list
)


class MealPlanCreateView(LoginRequiredMixin, View):
    """ Creates a meal plan for the current week. """

    def get(self, request):
        today = date.today()
        week_start = get_monday(today)

        plan, created = MealPlan.objects.get_or_create(
            user=request.user,
            week_start=week_start
        )

        if created:
            create_meal_slots(plan)

        return redirect("meal-plan-detail", plan_id=plan.id)


class MealPlanDetailView(LoginRequiredMixin, View):
    """ Displays a full weekly meal plan. """

    def get(self, request, plan_id):
        plan = get_object_or_404(
            MealPlan,
            id=plan_id,
            user=request.user
        )

        context = self._build_context(plan)
        return render(request, "meal_plan/meal_plan_detail.html", context)

    def _build_context(self, plan):
        """ Build template context data. """
        return {
            "plan": plan,
            "schedule": build_week_schedule(plan),
            "completion": calculate_completion(plan),
        }


class MealPlanNavigateView(LoginRequiredMixin, View):
    """ Navigate to previous or next week's meal plan. """

    def get(self, request, plan_id, direction):
        plan = get_object_or_404(
            MealPlan,
            id=plan_id,
            user=request.user
        )

        new_week = self._calculate_new_week(plan, direction)
        if not new_week:
            return redirect("meal-plan-detail", plan_id=plan.id)

        new_plan = self._get_or_create_plan(request.user, new_week)
        return redirect("meal-plan-detail", plan_id=new_plan.id)

    def _calculate_new_week(self, plan, direction):
        if direction == "prev":
            return plan.week_start - timedelta(days=7)
        if direction == "next":
            return plan.week_start + timedelta(days=7)
        return None

    def _get_or_create_plan(self, user, week_start):
        plan, created = MealPlan.objects.get_or_create(
            user=user,
            week_start=week_start
        )

        if created:
            create_meal_slots(plan)

        return plan


class MealSlotUpdateView(LoginRequiredMixin, View):
    """ Assign or change the recipe for one slot. """

    def get(self, request, slot_id):
        slot = get_object_or_404(
            MealSlot,
            id=slot_id,
            meal_plan__user=request.user
        )
        return render(request, "meal_plan/meal_slot_update.html", {
            "slot": slot,
            "recipes": Recipe.objects.all(),
        })

    def post(self, request, slot_id):
        slot = get_object_or_404(
            MealSlot,
            id=slot_id,
            meal_plan__user=request.user
        )

        recipe_id = request.POST.get("recipe_id")
        slot.recipe = Recipe.objects.get(id=recipe_id) if recipe_id else None
        slot.save()

        return redirect("meal-plan-detail", plan_id=slot.meal_plan.id)


class MealSlotClearView(LoginRequiredMixin, View):
    """ Remove a recipe from the slot. """

    def get(self, request, slot_id):
        slot = get_object_or_404(
            MealSlot,
            id=slot_id,
            meal_plan__user=request.user
        )

        slot.recipe = None
        slot.save()
        return redirect("meal-plan-detail", plan_id=slot.meal_plan.id)


class ShoppingListView(LoginRequiredMixin, View):
    """ Generate shopping list from meal plan. """

    def get(self, request, plan_id):
        plan = get_object_or_404(
            MealPlan,
            id=plan_id,
            user=request.user
        )

        slots = plan.entries.filter(recipe__isnull=False)
        organised = organise_shopping_list(
            extract_ingredients(slots)
        )

        return render(request, "meal_plan/shopping_list.html", {
            "plan": plan,
            "shopping_list": organised,
            "ingredients_count": sum(len(items) for _, items in organised),
        })


class MealSlotNotesView(LoginRequiredMixin, View):
    """ Update notes for a meal slot. """

    def post(self, request, slot_id):
        slot = get_object_or_404(
            MealSlot,
            id=slot_id,
            meal_plan__user=request.user
        )

        slot.notes = request.POST.get("notes", "")
        slot.save()

        messages.success(request, "Notes saved successfully!")
        return redirect("meal-plan-detail", plan_id=slot.meal_plan.id)


class MealPlanReuseLastWeekView(LoginRequiredMixin, View):
    """ Reuse meals from previous week's meal plan. """

    def post(self, request, plan_id):
        plan = get_object_or_404(
            MealPlan,
            id=plan_id,
            user=request.user
        )

        if not reuse_prev_week(plan):
            messages.warning(
                request,
                "No meals from last week available to reuse."
            )

        return redirect("meal-plan-detail", plan_id=plan.id)
