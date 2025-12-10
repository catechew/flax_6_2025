from random import randint, choice, sample 
from django.utils import timezone
from datetime import timedelta 

""" 
Recipe data generation for database seeding. 
"""

DISHES = [
            "Arrabbiata Pasta",
            "Lentil Bolognese",
            "Pasta Bake",
            "Spaghetti Bolognese",
            "Tomato Pasta",
            "Tuna Pasta",
            "Macaroni & Cheese",
            "Baked Four Cheese Mac",
            "Garlic Butter Macaroni",
            
            "Chicken Fried Rice",
            "Egg Fried Rice",
            "Lemon Herb Rice",
            "Nasi Lemak",
            "Thai Basil Rice",
            "Tofu Fried Rice",
            "Veggie Fried Rice",
            
            "Buldak Ramen",
            "Instant Noodles",
            "Mee Goreng",
            "Pad Thai",
            "Pot Noodle Upgrade",
            "Spicy Miso Ramen",
            
            "Beef Pho",
            "Chicken Noodle Soup",
            "Gyoza Soup",
            "Lemongrass Soup",
            "Pho",
            "Tomato Soup",
            "Tofu Pho",
            "Miso Ginger Noodle Soup",

            "Aloo Gobi",
            "Butter Chicken",
            "Chickpea Curry",
            "Katsu Curry",
            "Tarka Dal",

            "Breakfast Toast",
            "Honey Banana Toast",
            "Pancake Toast",

            "Brown Sugar Boba",
            "Bubble Tea",
            "Caramel Macchiato",
            "Chai Latte",
            "Coffee",
            "Detox Water",
            "Dragonfruit Smoothie",
            "Hot Chocolate",
            "Lemonade",
            "Mocha Frappé",
            "Oat Cappuccino",
            "Peach Iced Tea",
            "Raspberry Coconut Cooler",
            "Raspberry Ripple Milkshake",
            "Ribena Mocktail",
            "Strawberry Banana Smoothie",
            "Sweet Iced Tea",
            "Vanilla Matcha",
            "Very Berry Hibiscus Refresher",

            "Classic Cheeseburger",
            "Diner Style Cheeseburger",
            "Double Smashburger",
            "No Meat Burger",
            "Ranch Chicken Burger",
            "Veggie Bean Burger",

            "Baked Sea Bass with Wedges",
            "British Fish and Chips",
            "Cod & Chips",

            "Lemon Herb Steak",
            "Pan-Seared Steak",
            "Steak",

            "Chicken Fajitas",
            "Stir-fry",
            "Vegetable Stir-fry",

            "Baked Beans",
            "Garlic Butter Wedges",
            "Mashed Potatoes",
            "Oven Chips",
            "Potato Wedges",
            "Pub Style Mash",

            "Acai Bowl",
            "Breakfast Parfait",
            "Caesar Salad",
            "Greek Salad",
            "Halloumi Salad Bowl",

            "Apple Pie",
            "Banana Split",
            "Chocolate Banana Jar Cake",
            "Double Chocolate Parfait",
            "Microwave Mug Cake",
            "Nutella Cheesecake Cup",
            "Tanghulu",

            "Cereal Snack",
            "Overnight Oats",

            "Hummus",

            "Mushroom Risotto",
]

ADJECTIVES = [
    "Easy", "Quick", "Budget", "Simple", "Gordon Ramsey's", "Jamie Oliver's", "Cheap", 
    "Lazy", "Viral", "Microwave", "Leftover", "TikTok Style", "Comfort", 
    "Pinterest Worthy", "Creamy", "Vegan", "Light", "Special", "15 Minute", "Aesthetic", 
    "Homemade", "Zesty", "Rich", "Fresh", "Leftover Friendly", "Restaurant Style"
]

PROTEIN = [
    "Chicken Breast (2)", "Salmon Fillet (1)", "Minced Beef (500g)",
    "Tuna (1 can)", "Eggs (2)", "Halloumi (200g)", "Tofu (1 block)", 
    "Chickpeas (400g)", "Soya Nuggets (50g)"
]

VEGETABLES = [
    "Onion (1)", "Garlic (3 cloves)", "Bell Pepper (1)",
    "Spinach (1 handful)", "Broccoli (1 cup)", "Cherry Tomatoes (1 cup)",
    "Mushrooms (1 cup)", "Avocado (1)", "Cauliflower (2 cups)", 
    "Peas (1 cup)", "Cucumber (1)", "Carrot (2)"
]

FRUITS = [
    "Apple (1)", "Banana (1)", "Lemon (1)", "Strawberries (1 cup)", "Blueberries (1 box)"
]

GRAINS = [
    "Rice (1 cup)", "Penne Pasta (200g)", "Bread (2 slices)", "Flour (1 cup)"
]

DAIRY = [
    "Milk (1 cup)", "Butter (50g)", "Cheddar Cheese (1/4 cup)", "Yogurt (1/2 cup)"
]

PANTRY = [
    "Olive Oil (1 tbsp)", "Soy Sauce (1 tbsp)", "Salt (1 tsp)", "Pepper (3 tsp)", "Sugar (5 tbsp)"
]

HERBS_SPICES = [
    "Basil Leaves (1)", "Cilantro (1)", "Ginger (1 inch)", "Chili Flakes (10g)"
]

PREP_STEPS = [
    "Chop the onion and garlic",
    "Season ingredients with salt and pepper",
    "Preheat oven to 350°F",
    "Wash and prepare vegetables",
    "Whisk eggs and milk together",
    "Chop the onion and bell pepper",
    "Slice apples into thin cubes",
    "Marinate salmon with lemon zest, salt and pepper",
    "Whisk Coffee Powder and Milk"
]

COOK_STEPS = [
    "Heat oil in a pan over medium heat",
    "Add ingredients and cook until soft",
    "Bring water to a boil and add pasta",
    "Bake for 20 minutes until golden",
    "Simmer on low heat for 7 minutes",
    "Stir occasionally whilst cooking",
    "Mix garlic and soy sauce",
    "Season chicken with salt and pepper",
    "Fold in the dry ingredients",
    "Boil chicken in stock for 10 minutes"
]

FINISH_STEPS = [
    "Garnish with fresh herbs",
    "Let rest for 5 minutes before serving",
    "Taste and adjust seasoning",
    "Serve hot",
    "Garnish with fresh parsley",
    "Drizzle caramel sauce on top before serving",
    "Drizzle mayo and siracha on top"
]

class RecipeDataGenerator:
    """ Generates random recipe data for seeding. """

    @staticmethod
    def generate_title():
        """ Generate a random recipe tite. """
        if randint(0, 1):
            return f"{choice(ADJECTIVES)} {choice(DISHES)}"
        return choice(DISHES)
    
    @staticmethod
    def generate_date():
        """ Generate a random publication date within the last 2 years. """
        days_ago = randint(0, 730)
        return timezone.now().date() - timedelta(days=days_ago)
    
    @staticmethod
    def generate_time_component():
        """ Generate random hours and minutes for cooking time. """
        return randint(0, 2), randint(1, 60)
    
    @staticmethod
    def generate_ingredients():
        """ Generate a realistic ingredient list. """
        ingredients = (
            sample(PROTEIN, randint(1, 2)) +
            sample(VEGETABLES, randint(2, 3)) +
            sample(GRAINS, randint(1, 2)) +
            sample(DAIRY, randint(0, 2)) +
            sample(FRUITS, randint(0, 1)) +
            sample(PANTRY, randint(2, 3)) +
            sample(HERBS_SPICES, randint(0, 2))
        )
        return '\n'.join(ingredients)
    
    @staticmethod
    def generate_steps():
        """ Generate realistic cooking steps. """
        steps = (
            sample(PREP_STEPS, randint(1, 2)) +
            sample(COOK_STEPS, randint(2, 3)) +
            sample(FINISH_STEPS, randint(1, 2))
        )
        if "Serve hot" not in steps:
            steps.append("Serve hot")
        return '\n'.join(steps)
    
    @staticmethod
    def build_recipe_payload(title, prep, cook):
        prep_h, prep_m = prep
        cook_h, cook_m = cook

        return {
            "title": title,
            "publication_date": RecipeDataGenerator.generate_date(),
            "ingredients": RecipeDataGenerator.generate_ingredients(),
            "steps": RecipeDataGenerator.generate_steps(),
            "prep_time_hours": prep_h,
            "prep_time_minutes": prep_m,
            "cook_time_hours": cook_h,
            "cook_time_minutes": cook_m,
        }