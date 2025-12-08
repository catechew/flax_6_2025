from datetime import timedelta

""" 
Helper functions for meal plan operations. 
"""

def get_monday(date_obj):
    """ Return the Monday of the week for a given date. """
    return date_obj - timedelta(days=date_obj.weekday())

def calculate_completion(plan):
    """ Calculate meal plan completion percentage. """
    required_meals = ["breakfast", "lunch", "dinner"]
    required_slots = plan.entries.filter(meal_type__in=required_meals)
    filled = required_slots.filter(recipe__isnull=False).count()
    total = required_slots.count()
    
    return round((filled / total) * 100) if total else 0

def build_week_schedule(plan):
    """ Build structured schedule data for a meal plan. """
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
    """ Create empty slots for a new meal plan. """
    from recipes.models.meal_plan import MealSlot
    
    days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    meals = ["breakfast", "lunch", "dinner", "snack"]
    slots = [
        MealSlot(meal_plan=plan, day=day, meal_type=meal, recipe=None)
        for day in days
        for meal in meals
    ]
    MealSlot.objects.bulk_create(slots)

def reuse_prev_week(plan):
    """ Copy all entries from the previous week's meal plan. """
    prev_plan = _get_previous_week_plan(plan)
    if not prev_plan:
        return False
    
    if not _has_any_recipes(prev_plan):
        return False
    
    meals_copied = _copy_all_meal_slots(plan, prev_plan)
    return meals_copied > 0


def _get_previous_week_plan(plan):
    """ Get meal plan from previous week. """
    prev_week = plan.week_start - timedelta(days=7)
    try:
        return plan.user.meal_plans.get(week_start=prev_week)
    except plan.user.meal_plans.model.DoesNotExist:
        return None


def _has_any_recipes(prev_plan):
    """ Check if previous plan has any recipes. """
    return prev_plan.entries.filter(recipe__isnull=False).exists()

def _copy_all_meal_slots(plan, prev_plan):
    """ Copy all slots from previous plan. """
    results = [_copy_single_meal_slot(slot, prev_plan) for slot in plan.entries.all()]
    return sum(results)

def _copy_single_meal_slot(slot, prev_plan):
    """ Copy recipe and notes from matching previous slot. """
    prev_slot = _find_matching_slot(prev_plan, slot)
    if not prev_slot:
        return False
    
    slot.recipe = prev_slot.recipe
    slot.notes = prev_slot.notes
    slot.save()
    return prev_slot.recipe is not None


def _find_matching_slot(prev_plan, slot):
    """ Find slot in previous plan matching day and meal type. """
    return prev_plan.entries.filter(
        day=slot.day,
        meal_type=slot.meal_type
    ).first()

def calculate_meals_logged(plan):
    """
    Count how many of the key meals (breakfast, lunch, dinner)
    have been logged with recipes for the week.
    """
    meal_types = ["breakfast", "lunch", "dinner"]
    logged = plan.entries.filter(
        meal_type__in=meal_types,
        recipe__isnull=False
    ).count()
    total = 7 * len(meal_types)  # 7 days × 3 meals
    return logged, total