"""
Management command to seed the database with demo data.

This command creates a small set of named fixture users and then fills up
to ``USER_COUNT`` total users using Faker-generated data. Existing records
are left untouched—if a create fails (e.g., due to duplicates), the error
is swallowed and generation continues.
"""

from faker import Faker
from random import randint, random, choice, sample
from django.core.management.base import BaseCommand
from recipes.models import User, Recipe
from django.utils import timezone
from datetime import timedelta
import requests
from django.core.files.base import ContentFile
import os
from django.conf import settings


user_fixtures = [
    {'username': '@johndoe', 'email': 'john.doe@example.org', 'first_name': 'John', 'last_name': 'Doe'},
    {'username': '@janedoe', 'email': 'jane.doe@example.org', 'first_name': 'Jane', 'last_name': 'Doe'},
    {'username': '@charlie', 'email': 'charlie.johnson@example.org', 'first_name': 'Charlie', 'last_name': 'Johnson'},
]

class Command(BaseCommand):
    """
    Build automation command to seed the database with data.

    This command inserts a small set of known users (``user_fixtures``) and then
    repeatedly generates additional random users until ``USER_COUNT`` total users
    exist in the database. Each generated user receives the same default password.

    Attributes:
        USER_COUNT (int): Target total number of users in the database.
        RECIPE_COUNT (int): Target total numbers of recipes in the database. 
        DEFAULT_PASSWORD (str): Default password assigned to all created users.
        help (str): Short description shown in ``manage.py help``.
        faker (Faker): Locale-specific Faker instance used for random data.
    """

    USER_COUNT = 200
    RECIPE_COUNT = 500
    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data'

    def __init__(self, *args, **kwargs):
        """Initialize the command with a locale-specific Faker instance."""
        super().__init__(*args, **kwargs)
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        """
        Django entrypoint for the command.

        Runs the full seeding workflow and stores ``self.users`` for any
        post-processing or debugging (not required for operation).
        """
        self.create_users()
        self.users = User.objects.all()
        self.create_recipes()

    def create_users(self):
        """
        Create fixture users and then generate random users up to USER_COUNT.

        The process is idempotent in spirit: attempts that fail (e.g., due to
        uniqueness constraints on username/email) are ignored and generation continues.
        """
        self.generate_user_fixtures()
        self.generate_random_users()

    def generate_user_fixtures(self):
        """Attempt to create each predefined fixture user."""
        for data in user_fixtures:
            # Make @johndoe an admin user 
            if data["username"] == "@johndoe":
                try:
                    user = User.objects.create_superuser(
                        username=data["username"],
                        email=data["email"],
                        password=Command.DEFAULT_PASSWORD,
                        first_name=data["first_name"],
                        last_name=data["last_name"],
                    )
                    user.is_staff = True
                    user.save()
                except Exception: 
                    pass
            else:
                self.try_create_user(data)        

    def generate_random_users(self):
        """
        Generate random users until the database contains USER_COUNT users.

        Prints a simple progress indicator to stdout during generation.
        """
        user_count = User.objects.count()
        while  user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            self.generate_user()
            user_count = User.objects.count()
        print("User seeding complete.      ")

    def generate_user(self):
        """
        Generate a single random user and attempt to insert it.

        Uses Faker for first/last names, then derives a simple username/email.
        """
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = create_email(first_name, last_name)
        username = create_username(first_name, last_name)
        self.try_create_user({'username': username, 'email': email, 'first_name': first_name, 'last_name': last_name})
       
    def try_create_user(self, data):
        """
        Attempt to create a user and ignore any errors.

        Args:
            data (dict): Mapping with keys ``username``, ``email``,
                ``first_name``, and ``last_name``.
        """
        try:
            self.create_user(data)
        except:
            pass

    def create_user(self, data):
        """
        Create a user with the default password.

        Args:
            data (dict): Mapping with keys ``username``, ``email``,
                ``first_name``, and ``last_name``.
        """
        User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=Command.DEFAULT_PASSWORD,
            first_name=data['first_name'],
            last_name=data['last_name'],
        )

    def create_recipes(self):
        """Generate random recipes up to the recipe count."""
        recipe_count = Recipe.objects.count()
        users = list(User.objects.all())

        if not users:
            print("No users found. Cannot create recipes.")
            return 

        while recipe_count < self.RECIPE_COUNT:
            print(f"Seeding recipe {recipe_count}/{self.RECIPE_COUNT}", end='\r')
            self.generate_recipe(users)
            recipe_count = Recipe.objects.count()
        print("Recipe seeding complete. ")

    def generate_recipe(self, users):
        """Generate a random recipe."""
        title = self.generate_recipe_title()
        author = choice(users)
        publication_date = self.generate_random_date()
        ingredients = self.generate_random_ingredients()
        steps = self.generate_random_steps()
        prep_time_hours = self.generate_random_hours()
        prep_time_minutes = self.generate_random_minutes()
        cook_time_hours = self.generate_random_hours()
        cook_time_minutes = self.generate_random_minutes()
        course_tags = self.generate_course_tags()
        cuisine_tags = self.generate_cuisine_tags()
        dietary_tags = self.generate_dietary_tags()
        other_tags = self.generate_other_tags()

        # Download random food image 
        image_content = None
        image_filename = None
        image_content, image_filename = self.download_random_food_image(title=title)


        self.try_create_recipe({
            'title': title,
            'author': author,
            'publication_date': publication_date,
            'ingredients' : ingredients,
            'steps': steps,
            'prep_time_hours': prep_time_hours,
            'prep_time_minutes': prep_time_minutes,
            'cook_time_hours': cook_time_hours,
            'cook_time_minutes': cook_time_minutes,
            'course_tags': course_tags,
            'cuisine_tags': cuisine_tags,
            'dietary_tags': dietary_tags,
            'other_tags': other_tags,
            'image_content': image_content,
            'image_filename': image_filename,
        })

    def generate_recipe_title(self):
        """Generate a recipe title for university students."""
        dishes = [
            "Pesto pasta", "Buldak Ramen", "Stir-fry", "Fried Rice", 
            "Vegan Katsu Curry", "Tanghulu", "Salmon Rice Bowl", "Quesadilla", 
            "Vegan Sausage Wrap", "Ceaser salad", "Tomato soup", "Tofu Thai Curry", "Omelette", 
            "Egg Benedicts", "Beans on Toast", "Jacket Potato", "Trending Acai Bowl",
            "Microwave Mug Cake", "Overnight Oats", "Smoothie Bowl",
            "Grilled Cheese", "Tuna Pasta", "Pizza Toast", "Chocolate Chip Muffins", 
            "Butter Chicken", "Aloo Gobi", "Pho", "Spaghetti Bolognese", "Chili Con Carne", 
            "Tarka Dal", "Chicken Fajitas", "Cauliflower Risotto", "Macaroni & Cheese", 
            "Tuna Melt", "Hummus", "Sweet & Sour Sauce", "Tofu Fried Rice", "Cheeseburger", 
            "Gyoza Soup", "Halloumi Wrap", "Swiss Steak", "Breakfast Wrap", "Chilli Cheese Toast", 
            "Chai Latte", "Vanilla Matcha", "Hot Chocolate", "Strawberry Banana Smoothie",
            "Detox Water", "Ribena Mocktail", "Blueberry Cheesecake", "Pan-fried Salmon", 
            "Margherita Pizza", "Mushroom Curry", "Tiramisu", "Breakfast Parfait", 
            "S'mores dip", "Lentil Bolognese", "Pad Thai", "Raspberry Ripple Milkshake", 
            "Mocha frappé", "Mashed Potatoes", "Fish and Chips", "Mushy Peas", "Mee Goreng",
            "Boba at home", "Nasi Lemak", "Lobster", "Apple Pie", "Banana Split"      
            ]
        
        adjectives = [
            "Easy", "Quick", "Budget", "Simple", "Cheap",
            "5-Minute", "Dorm Room", "One-Pot", "Viral",
            "Microwave", "Leftover", "Late Night",
            "Study Snack", "Protein-Packed", "Vegetarian",
            "Meal Prep", "Batch Cook", "Freezer Friendly",
            "TikTok", "Instagram-Worthy", "Comfort Food",
            "Pinterest Worthy", "Spicy", "Creamy", 
            "Healthy", "High Protein", "Low Carb",
            "Trending", "Aesthetic",
            "Weekend", "Brunch", "Midweek", "Fancy",
            "Gourmet", "Homemade", "Restaurant-Style", "Summer", 
            "Italian", "Asian", "Mediterranean", 
            "Michelin Style", "Vegan", "Gluten Free", "Hot", 
            "Cold"
        ]
        
        if randint(0, 1):
            return f"{choice(adjectives)} {choice(dishes)}"
        else:
            return f"{choice(dishes)}"
    
    def generate_random_date(self):
        """Generate a random publication date within the last 2 years."""
        days_limit = randint(0, 730)
        return timezone.now().date() - timedelta(days=days_limit)
    
    def generate_random_ingredients(self):
        """Generate a realistic list of random ingredients"""
        protein = [
            "Chicken Breast (2)",
            "Salmon Fillet (1)",
            "Minced Beef (500g)",
            "Tuna (1 can)",
            "Eggs (2)",
            "Halloumi (200g)",
            "Tofu (1 block)",
        ]

        vegetables = [
            "Onion (1)",
            "Garlic (3 cloves)",
            "Bell Pepper (1)",
            "Spinach (1 handful)",
            "Broccoli (1 cup)",
            "Cherry Tomatoes (1 cup)",
            "Mushrooms (1 cup)",
            "Avocado (1)",
        ]

        fruits = [
            "Apple (1)",
            "Banana (1)",
            "Lemon Zest (1)",
            "Strawberries (1 cup)",
        ]

        grains = [
            "Rice (1 cup)",
            "Penne Pasta (200g)",
            "Bread (2 slices)",
            "Flour (1 cup)",
        ]

        dairy = [
            "Milk (1/2 cup)",
            "Butter (50g)",
            "Cheddar Cheese (1/4 cup)",
            "Yogurt (1/2 cup)",
        ]

        pantry = [
            "Olive Oil (1 tbsp)",
            "Soy Sauce (1 tbsp)",
            "Salt (1 tsp)",
            "Black Pepper (1/2 tsp)",
            "Sugar (1 tbsp)",
        ]

        herbs_spices = [
            "Basil Leaves",
            "Cilantro",
            "Ginger (1 inch)",
            "Chili Flakes",
        ]

        # Pick a realistic mix
        ingredients = (
            sample(protein, randint(1, 2)) +
            sample(vegetables, randint(2, 3)) +
            sample(grains, randint(1, 2)) +
            sample(dairy, randint(0, 2)) +
            sample(fruits, randint(0, 1)) +
            sample(pantry, randint(2, 3)) +
            sample(herbs_spices, randint(0, 2))
        )

        return '\n'.join(ingredients)
    
    def generate_random_steps(self):
        """Generate a realistic list of cooking steps"""

        prep_steps = [
            "Chop the onion and garlic",
            "Season ingredients with salt and pepper",
            "Preheat oven to 350°F",
            "Wash and prepare vegetables",
            "Whisk eggs and milk together",
            "Chop the onion and bell pepper",
            "Slice apples into thin cubes",
            "Marinate salmon with lemon zest, salt and pepper",
        ]

        cook_steps = [
            "Heat oil in a pan over medium heat",
            "Add ingredients and cook until soft",
            "Bring water to a boil and add pasta",
            "Bake for 20 minutes until golden",
            "Simmer on low heat for 7 minutes",
            "Stir occasionally whilst cooking",
            "Mix garlic and soy sauce",
            "Season chicken with salt and pepper",
            "Fold in the dry ingredients", 
            "Boil chicken in stock for 10 minutes",
        ]

        finish_steps = [
            "Garnish with fresh herbs",
            "Let rest for 5 minutes before serving",
            "Taste and adjust seasoning",
            "Serve hot",
            "Garnish with fresh parsley",
            "Drizzle caramel sauce on top before serving",
            "Drizzle mayo and siracha on top",
        ]

        steps = (
            sample(prep_steps, randint(1, 2)) +
            sample(cook_steps, randint(2, 3)) +
            sample(finish_steps, randint(1, 2))
        )

        if "Serve hot" not in steps:
            steps.append("Serve hot") # So users never see a recipe that ends mid-process

        return '\n'.join(steps)
       
    
    def generate_random_hours(self):
        """Generate random hour"""
        rand_hour = randint(0,2)
        return rand_hour
    
    def generate_random_minutes(self):
        """Generate random minute"""
        rand_min = randint(1,60)
        return rand_min
    
    def generate_course_tags(self):
        """Generate random course tags"""
        course_options = ['dessert', 'main', 'appetiser', 'breakfast', 'snack']
        num_tags = randint(0,2)
        if num_tags == 0:
            return ''
        selected = sample(course_options, num_tags)
        return ','.join(selected)
    
    def generate_cuisine_tags(self):
        """Generate random cuisine tags"""
        cuisine_options = ['Japanese', 'Italian', 'Chinese', 'Asian', 'Persian', 'Jamaican', 'Western', 'British', 'Lebanese','Middle-Eastern']
        num_tags = randint(0,2)
        if num_tags == 0:
            return ''
        selected = sample(cuisine_options, num_tags)
        return ','.join(selected)
    
    def generate_dietary_tags(self):
        """Generate random dietary tags"""
        dietary_options = ['vegetarian', 'vegan', 'halal', 'kosher', 'gluten-free', 'dairy-free']
        num_tags = randint(0,2)
        if num_tags == 0:
            return ''
        selected = sample(dietary_options, num_tags)
        return ','.join(selected)
    
    def generate_other_tags(self):
        """Generate random other tags"""
        other_options = ['high protein', 'low calorie', 'low carb', 'quick', 'budget', "quick easy", "budget-friendly", "cheap", "simple",
            "viral trendy", "instagram worthy aesthetic", "5-minute",
            "one pot", "leftover-friendly", "meal-prep batch",
            "protein-packed filling", "vegetarian healthy", "vegan plant based",
            "late-night comfort", "study snack energy", "cozy",
            "freezer friendly", "restaurant style fancy", "homemade",
            "spicy", "creamy", "crispy","trending", 
            "tiktok famous", "brunch-worthy special",
            "microwave easy", "dorm room friendly", "high protein low calories",
            "italian", "indian", "vietnamese",
            "chinese takeout", "mediterranean", "summer",
            "gourmet", "weekend treat", "midweek"]
        num_tags = randint(0,2)
        if num_tags == 0:
            return ''
        selected = sample(other_options, num_tags)
        return ','.join(selected)
    
    def get_dish_type_from_title(self, title):
        """Map recipe title to Foodish API dish type."""
        title_lower = title.lower()

        # Foodish API available dishes
        dish_mapping = {
            'pasta': ['pasta', 'spaghetti', 'penne', 'macaroni', 'bolognese'],
            'rice': ['rice', 'fried rice', 'rice bowl', 'biryani', 'nasi lemak'],
            'burger': ['burger', 'cheeseburger'],
            'pizza': ['pizza', 'margherita'],
            'dessert': ['dessert', 'cake', 'cheesecake', 'tiramisu', 'muffin','s\'mores', 'parfait'],
            'curry': ['curry', 'butter chicken', 'aloo gobi', 'dal', 'katsu'],
            'soup': ['soup', 'pho', 'gyoza soup'],
            'wrap': ['wrap', 'quesadilla', 'fajitas'],
            'salad': ['salad', 'bowl', 'acai'],
            'toast': ['toast', 'beans on toast', 'cheese toast', 'pizza toast'],
            'drink': ['smoothie', 'latte', 'chocolate', 'mocktail','milkshake', 'frappé', 'boba'],
        }

        # Check if title contains any keywords
        for image_name, keywords in dish_mapping.items():
            for keyword in keywords:
                if keyword in title_lower:
                    return image_name

        # Default to default image
        return 'default'

    
    def download_random_food_image(self, title=None):
        """Select a local food placeholder image based on recipe title"""
        try:
            # Get the image type from title
            image_type = 'default'
            if title:
                image_type = self.get_dish_type_from_title(title)

            # Build API URL
            image_path = f'static/images/food_placeholders/{image_type}.jpg'

            # Check if the file exists
            full_path = os.path.join(settings.BASE_DIR, image_path)

            if os.path.exists(full_path):
                with open(full_path, 'rb') as f:
                    image_content = ContentFile(f.read())
                    filename = f"recipe_{image_type}_{randint(1000,9999)}.jpg"
                    return image_content, filename
            
            else:
                # If specific image doesn't exist, try default
                default_path = os.path.join(settings.BASE_DIR, 'static/images/food_placeholders/default.jpg')
                if os.path.exists(default_path):
                    with open(default_path, 'rb') as f:
                        image_content = ContentFile(f.read())
                        filename = f"recipe_default_{randint(1000,9999)}.jpg"
                        return image_content, filename

        except Exception as e:
            print(f"Error loading placeholder image: {e}")
            pass
        
        return None, None
    
    def try_create_recipe(self, data):
        """Attempt to create a recipe."""
        try:
            recipe = Recipe.objects.create(
                title=data['title'],
                author=data['author'],
                publication_date=data['publication_date'],
                ingredients=data['ingredients'],
                steps=data['steps'],
                prep_time_hours=data['prep_time_hours'],
                prep_time_minutes=data['prep_time_minutes'],
                cook_time_hours=data['cook_time_hours'],
                cook_time_minutes=data['cook_time_minutes'],
                course_tags=data['course_tags'],
                cuisine_tags=data['cuisine_tags'],
                dietary_tags=data['dietary_tags'],
                other_tags=data['other_tags'],
            )
            # Save image if available
            if data['image_content'] and data['image_filename']:
                recipe.image.save(data['image_filename'], data['image_content'], save=True)
        except:
            print(f"Error creating recipe: {e}")  # THIS LINE - temporarily add this
            pass
    
                              
def create_username(first_name, last_name):
    """
    Construct a simple username from first and last names.

    Args:
        first_name (str): Given name.
        last_name (str): Family name.

    Returns:
        str: A username in the form ``@{firstname}{lastname}`` (lowercased).
    """
    return '@' + first_name.lower() + last_name.lower()

def create_email(first_name, last_name):
    """
    Construct a simple example email address.

    Args:
        first_name (str): Given name.
        last_name (str): Family name.

    Returns:
        str: An email in the form ``{firstname}.{lastname}@example.org``.
    """
    return first_name + '.' + last_name + '@example.org'