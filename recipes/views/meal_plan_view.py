from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import date, timedelta

from recipes.models.meal_plan import MealPlan, MealSlot
from recipes.models.recipe import Recipe

def get_monday(d):
    """Return the Monday of the week for a given date"""
    return d - timedelta(days=d.weekday())

class MealPlanCreateView(LoginRequiredMixin, View):
    """
    Creates a meal plan for the current week
    If it already exists, redirect to detail view
    """
    def get(self, request):
        print("=" * 50)
        print("🔍 MEAL PLAN CREATE VIEW CALLED!")
        print(f"User: {request.user.username}")
        print("=" * 50)
        
        today = date.today()
        week_start = get_monday(today)

        plan, created = MealPlan.objects.get_or_create(
            user=request.user,
            week_start=week_start
        )
        
        print(f"Plan ID: {plan.id}, Created: {created}")

        if created:
            # Create empty day slots for the whole week
            days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
            meals = ["breakfast", "lunch", "dinner", "snack"]

            for d in days:
                for m in meals:
                    MealSlot.objects.create(
                        meal_plan=plan, 
                        day=d, 
                        meal_type=m, 
                        recipe=None
                    )
            print("✅ Created 28 new meal slots")
        
        print(f"Redirecting to meal-plan-detail with plan_id={plan.id}")
        return redirect("meal-plan-detail", plan_id=plan.id)

class MealPlanDetailView(LoginRequiredMixin, View):
    """Show the whole weekly plan in a calendar layout"""
    def get(self, request, plan_id):
        print("=" * 50)
        print("🔍 MEAL PLAN DETAIL VIEW CALLED!")
        print(f"Plan ID: {plan_id}")
        print(f"User: {request.user.username}")
        print("=" * 50)
        
        plan = get_object_or_404(MealPlan, id=plan_id, user=request.user)
        
        print(f"✅ Plan found: {plan}")
        
        # Get all slots
        all_slots = plan.entries.all()
        print(f"✅ Found {all_slots.count()} slots")
        
        # Define days and meals
        days = [
            ('mon', 'Monday'),
            ('tue', 'Tuesday'),
            ('wed', 'Wednesday'),
            ('thu', 'Thursday'),
            ('fri', 'Friday'),
            ('sat', 'Saturday'),
            ('sun', 'Sunday'),
        ]
        meals = ['breakfast', 'lunch', 'dinner', 'snack']
        
        # Build the schedule - list of day rows
        schedule = []
        for day_code, day_name in days:
            row = {
                'day_code': day_code,
                'day_name': day_name,
                'slots': {}
            }
            for meal in meals:
                slot = all_slots.filter(day=day_code, meal_type=meal).first()
                row['slots'][meal] = slot
            schedule.append(row)
        
        print(f"✅ Built schedule with {len(schedule)} days")

        context = {
            "plan": plan,
            "schedule": schedule,
            "meals": meals,
        }
        
        print("✅ Rendering meal_plan_detail.html")
        print("=" * 50)
        
        return render(request, "meal_plan_detail.html", context)

class MealSlotUpdateView(LoginRequiredMixin, View):
    """Assign or change the recipe for one slot."""
    def get(self, request, slot_id):
        slot = get_object_or_404(MealSlot, id=slot_id, meal_plan__user=request.user)

        recipes = Recipe.objects.all()

        return render(request, "meal_slot_update.html", {
            "slot": slot,
            "recipes": recipes,
        })
    
    def post(self, request, slot_id):
        slot = get_object_or_404(MealSlot, id=slot_id, meal_plan__user=request.user)

        recipe_id = request.POST.get("recipe_id")
        slot.recipe = Recipe.objects.get(id=recipe_id)
        slot.save()

        return redirect("meal-plan-detail", plan_id=slot.meal_plan.id)