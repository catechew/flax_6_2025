""" Helper functions for meal plan operations. """

from datetime import timedelta

def get_monday(date_obj):
    """Return the Monday of the week for a given date."""
    return date_obj - timedelta(days=date_obj.weekday())

def calculate_completion(plan):
    """
    Calculate meal plan completion percentage.
    
    Args:
        plan: MealPlan instance
        
    Returns:
        int: Completion percentage (0-100)
    """
    required_meals = ["breakfast", "lunch", "dinner"]
    required_slots = plan.entries.filter(meal_type__in=required_meals)
    
    filled = required_slots.filter(recipe__isnull=False).count()
    total = required_slots.count()
    
    return round((filled / total) * 100) if total else 0

def build_week_schedule(plan):
    """
    Build structured schedule data for a meal plan.
    
    Args:
        plan: MealPlan instance
        
    Returns:
        list: Schedule with day and slot data
    """
    days = _get_weekdays()
    meals = ['breakfast', 'lunch', 'dinner', 'snack']
    all_slots = plan.entries.all()
    schedule = []
    
    for index, (day_code, day_name) in enumerate(days):
        day_data = _build_day_data(plan, day_code, day_name, index)
        _add_meal_slots(day_data, all_slots, meals)
        schedule.append(day_data)
    
    return schedule

def _get_weekdays():
    """ Return list of weekday tuples. """
    return [
        ('mon', 'Monday'), ('tue', 'Tuesday'), ('wed', 'Wednesday'),
        ('thu', 'Thursday'), ('fri', 'Friday'), ('sat', 'Saturday'),
        ('sun', 'Sunday')
    ]

def _build_day_data(plan, day_code, day_name, index):
    """ Build data structure for a single day. """
    current_date = plan.week_start + timedelta(days=index)
    return {
        'day_code': day_code,
        'day_name': day_name,
        'day_date': current_date,
        'slots': {}
    }

def _add_meal_slots(day_data, all_slots, meals):
    """ Add meal slots to day data. """
    for meal in meals:
        slot = all_slots.filter(
            day=day_data['day_code'],
            meal_type=meal
        ).first()
        day_data['slots'][meal] = slot


def create_meal_slots(plan):
    """
    Create empty slots for a new meal plan.
    
    Args:
        plan: MealPlan instance
    """
    from recipes.models.meal_plan import MealSlot
    
    days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    meals = ["breakfast", "lunch", "dinner", "snack"]
    
    for day in days:
        for meal in meals:
            MealSlot.objects.create(
                meal_plan=plan,
                day=day,
                meal_type=meal,
                recipe=None
            )

def calculate_statistics(plan):
    """
    Calculate meal plan statistics.
    
    Args:
        plan: MealPlan instance
        
    Returns:
        dict: Statistics including filled slots and unique recipes
    """
    filled_slots = plan.entries.filter(
        recipe__isnull=False
    ).count()
    
    unique_recipes = plan.entries.filter(
        recipe__isnull=False
    ).values('recipe').distinct().count()
    
    return {
        'filled_slots': filled_slots,
        'unique_recipes': unique_recipes
    }