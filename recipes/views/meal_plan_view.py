from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import date, timedelta

from recipes.models.meal_plan import MealPlan, MealSlot
from recipes.models.recipe import Recipe
from collections import defaultdict
from django.contrib import messages

def get_monday(d):
    """Return the Monday of the week for a given date"""
    return d - timedelta(days=d.weekday())

class MealPlanCreateView(LoginRequiredMixin, View):
    """
    Creates a meal plan for the current week.
    If it already exists, redirect user to detail view.
    """
    def get(self, request):   
        today = date.today()
        week_start = get_monday(today)

        plan, created = MealPlan.objects.get_or_create(
            user=request.user,
            week_start=week_start
        )
        
        if created:
            # Create empty day slots for the entire 7 day week
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

        return redirect("meal-plan-detail", plan_id=plan.id)

class MealPlanDetailView(LoginRequiredMixin, View):
    """ Handles the display of a full weekly meal plan. """

    def get(self, request, plan_id):
        # Fetch the meal plan belonging to the logged in user
        plan = get_object_or_404(MealPlan, id=plan_id, user=request.user)
        all_slots = plan.entries.all()

        days = [
            ('mon', 'Monday'),
            ('tue', 'Tuesday'),
            ('wed', 'Wednesday'),
            ('thu', 'Thursday'),
            ('fri', 'Friday'),
            ('sat', 'Saturday'),
            ('sun', 'Sunday'),
        ]
        # Types of meals a day contains
        meals = ['breakfast', 'lunch', 'dinner', 'snack']

        schedule = []

        for index, (day_code, day_name) in enumerate(days):
            current_date = plan.week_start + timedelta(days=index)

            row = {
                'day_code': day_code,
                'day_name': day_name,
                'day_date': current_date,
                'slots': {} # Container for breakfast/lunch/dinner/snack entries
            }
            
            # Attach the corresponding MealSlot for each meal type
            for meal in meals:
                slot = all_slots.filter(day=day_code, meal_type=meal).first()
                row['slots'][meal] = slot

            schedule.append(row)

        # Calculate statistics 
        filled_slots = all_slots.filter(recipe__isnull=False).count()
        unique_recipes = all_slots.filter(recipe__isnull=False).values('recipe').distinct().count()
        completion = round((filled_slots / 28) * 100) if filled_slots > 0 else 0

        return render(request, "meal_plan_detail.html", {
            "plan": plan,
            "schedule": schedule,
            "meals": meals,
            "filled_slots": filled_slots,
            "unique_recipes": unique_recipes,
            "completion": completion,
        })
    
class MealPlanNavigateView(LoginRequiredMixin, View):
    """ 
    Navigate to previous or next week's meal plan. 
    URL examples:
    /meal-plan/1/prev/
    /meal-plan/1/next/
    """
    def get(self, request, plan_id, direction):
        plan = get_object_or_404(MealPlan, id=plan_id, user=request.user)

        if direction == "prev":
            new_week = plan.week_start - timedelta(days=7)
        elif direction == "next":
            new_week = plan.week_start + timedelta(days=7)
        else:
            return redirect("meal-plan-detail", plan_id=plan.id)

        # Get plan for new week or create if it does not exist. 
        new_plan, created = MealPlan.objects.get_or_create(
            user=request.user,
            week_start=new_week
        )

        # If brand new meal plan: create 28 slots
        if created:
            days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
            meals = ["breakfast", "lunch", "dinner", "snack"]
            for d in days:
                for m in meals:
                    MealSlot.objects.create(
                        meal_plan=new_plan,
                        day=d,
                        meal_type=m,
                        recipe=None
                    )

        return redirect("meal-plan-detail", plan_id=new_plan.id)

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

        # Handle empty recipe selection (remove meal choice)
        if recipe_id:
            slot.recipe = Recipe.objects.get(id=recipe_id)
        else:
            slot.recipe = None
        
        slot.save()

        return redirect("meal-plan-detail", plan_id=slot.meal_plan.id)

class MealSlotClearView(LoginRequiredMixin, View):
    """Remove a recipe from the slot and make it empty."""
    def get(self, request, slot_id):
        slot = get_object_or_404(MealSlot, id=slot_id, meal_plan__user=request.user)

        slot.recipe = None
        slot.save()

        return redirect("meal-plan-detail", plan_id=slot.meal_plan.id)
    
class ShoppingListView(LoginRequiredMixin, View):
    """ Generate shopping list from meal plan """
    def get(self, request, plan_id):
        plan = get_object_or_404(MealPlan, id=plan_id, user=request.user)
        slots = plan.entries.filter(recipe__isnull=False)
    
        # Group ingredients by category
        shopping_list = defaultdict(list)
    
        for slot in slots:
            recipe = slot.recipe
            for ingredient in recipe.ingredients.split('\n'):
                ingredient = ingredient.strip()
                if ingredient:
                    category = self.categorise_ingredient(ingredient)
                    shopping_list[category].append({
                        'item': ingredient,
                        'recipe': recipe.title,
                        'day': slot.get_day_display(),
                        'meal': slot.get_meal_type_display()
                    })
    
        # Consolidate duplicates
        organised_list = {}
        for category, items in shopping_list.items():
            organised_list[category] = self.consolidate_items(items)
    
        # Define shopping flow order (matches typical grocery store layout)
        category_order = [
            '🥬 Vegetables',
            '🍎 Fruits',
            '🥩 Meat & Poultry',
            '🐟 Seafood',
            '🧀 Dairy & Eggs',
            '🌾 Grains & Pasta',
            '🧂 Condiments',
            '🌶️ Spices & Herbs',
            '🛒 Other Items',
        ]
    
        # Sort categories by defined order
        sorted_list = []
        for category in category_order:
            if category in organised_list:
                sorted_list.append((category, organised_list[category]))
    
        ingredients_count = sum(len(items) for items in organised_list.values())

        return render(request, 'shopping_list.html', {
            'plan': plan,
            'shopping_list': sorted_list,  # ← Changed from organised_list to sorted_list
            'ingredients_count': ingredients_count
        })
        
    def categorise_ingredient(self, ingredient):
        """Categorise ingredient by type"""
        ingredient_lower = ingredient.lower()
        
        if any(word in ingredient_lower for word in ['chicken', 'beef']):
            return '🥩 Meat & Poultry'
        elif any(word in ingredient_lower for word in ['salmon', 'tuna']):
            return '🐟 Seafood'
        elif any(word in ingredient_lower for word in ['cheese', 'cheddar', 'butter', 'milk', 'egg', 'halloumi', 'tofu', 'bread']):
            return '🧀 Dairy & Eggs'
        elif any(word in ingredient_lower for word in ['avocado', 'onion', 'garlic', 'tomatoes', 'lemon', 'spinach', 'ginger', 'broccoli', 'bell pepper', 'mushrooms']):
            return '🥬 Vegetables'
        elif any(word in ingredient_lower for word in ['apple', 'banana', 'lemon', 'strawberries']):
            return '🍎 Fruits'
        elif any(word in ingredient_lower for word in ['rice', 'flour', 'penne', 'pasta', 'beans']):
            return '🌾 Grains & Pasta'
        elif any(word in ingredient_lower for word in ['black pepper', 'basil', 'leaves', 'cilantro', 'chili']):
            return '🌶️ Spices & Herbs'
        elif any(word in ingredient_lower for word in ['oil', 'sugar', 'sauce', 'soy', 'salt']):
            return '🧂 Condiments'
        else:
            return '🛒 Other Items'
    
    def consolidate_items(self, items):
        """Group identical items and calculate total quantities"""
        from recipes.views.recipe_detail_view import scale_ingredient
        
        consolidated = defaultdict(lambda: {'count': 0, 'recipes': [], 'base_item': None})
        
        for item in items:
            # Extract base ingredient name (without quantity)
            ingredient = item['item']
            key = ingredient.lower()
            
            if consolidated[key]['base_item'] is None:
                consolidated[key]['base_item'] = ingredient
            
            consolidated[key]['count'] += 1
            consolidated[key]['recipes'].append(f"{item['day']} {item['meal']}: {item['recipe']}")
    
        # Calculate scaled totals
        result = []
        for key, data in consolidated.items():
            ingredient = data['base_item']
            count = data['count']
            
            if count > 1:
                # Scale the ingredient by the count
                scaled_ingredient = scale_ingredient(ingredient, count)
                result.append({
                    'item': scaled_ingredient,
                    'count': count,
                    'original': ingredient,
                    'recipes': data['recipes']
                })
            else:
                result.append({
                    'item': ingredient,
                    'count': 1,
                    'original': ingredient,
                    'recipes': data['recipes']
                })
        
        return result

class MealSlotNotesView(LoginRequiredMixin, View):
    """Update notes for a meal slot (for additional snacks/notes)"""
    def post(self, request, slot_id):
        slot = get_object_or_404(MealSlot, id=slot_id, meal_plan__user=request.user)
        
        notes = request.POST.get("notes", "")
        slot.notes = notes
        slot.save()
        
        messages.success(request, "Notes saved successfully!")
        return redirect("meal-plan-detail", plan_id=slot.meal_plan.id)    