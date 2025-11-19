"""
Management command to seed the database with demo data.

This command creates a small set of named fixture users and then fills up
to ``USER_COUNT`` total users using Faker-generated data. Existing records
are left untouched—if a create fails (e.g., due to duplicates), the error
is swallowed and generation continues.
"""

from faker import Faker
from random import randint, random, choice
from django.core.management.base import BaseCommand, CommandError
from recipes.models import User, Recipe
from django.utils import timezone
from datetime import timedelta

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
        adjectives = self.generate_adjectives()
        author = choice(users)
        publication_date = self.generate_random_date()

        self.try_create_recipe({
            'title': title,
            'adjectives': adjectives,
            'author': author,
            'publication_date': publication_date
        })

    def generate_recipe_title(self):
        """Generate a recipe title for university students."""
        dishes = [
            "Pesto pasta", "Michelin Style Buldak Ramen", "Stir-fry", "Fried Rice", 
            "Vegan Katsu Curry", "Tanghulu", "Noodles", "Salmon Rice Bowl", "Quesadilla", 
            "Vegan Sausage Wrap", "Ceaser salad", "Tomato soup", "Red Thai Curry", "Omelette", 
            "Egg Benedicts", "Beans on Toast", "Jacket Potato", "Trending Acai Bowl",
            "Microwave Mug Cake", "Viral Overnight Oats", "Smoothie Bowl",
            "Grilled Cheese", "Tuna Pasta", "Pizza Toast", "Chocolate Chip Muffins", 
            "Butter Chicken", "Aloo Gobi", "Pho", "Spaghetti Bolognese", "Chili Con Carne", 
            "Tarka Dal", "Chicken Fajitas", "Cauliflower Risotto", "Macaroni & Cheese", 
            "Tuna Melt", "Hummus", "Sweet & Sour Sauce", "Tofu Fried Rice", "Cheeseburger", 
            "Gyoza Soup", "Halloumi Wrap", "Beef Steak", "Breakfast Wrap", "Chilli Cheese Toast", 
            "Chai Latte", "Viral Vanilla Matcha", "Hot Chocolate", "Strawberry Banana Smoothie",
            "Detox Water", "Ribena Mocktail", "Bluberry Cheesecake"        
            ]
        
        adjectives = [
            "Easy", "Quick", "Budget", "Simple", "Cheap",
            "5-Minute", "Dorm Room", "One-Pot", 
            "Microwave", "Leftover", "Late Night",
            "Study Snack", "Protein-Packed", "Vegetarian",
            "Meal Prep", "Batch Cook", "Freezer-Friendly",
            "Viral TikTok", "Instagram-Worthy", "Comfort Food",
            "Spicy", "Creamy", "Crispy", "Fresh",
            "Healthy", "High-Protein", "Low-Carb",
            "Trending", "Aesthetic", "Cozy",
            "Weekend", "Brunch", "Midweek", "Fancy",
            "Gourmet", "Homemade", "Restaurant-Style", "Summer", 
            "Italian", "Indian", "Vietnamese", "Chinese", "Mediterranean"
        ]
        
        if randint(0, 1):
            return f"{choice(adjectives)} {choice(dishes)}"
        else:
            return f"{choice(dishes)}"
    
    def generate_adjectives(self):
        """Generate recipe tags to describe meals."""
        adjective_options = [
            "quick easy", "budget-friendly", "cheap", "simple",
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
            "gourmet", "weekend treat", "midweek"
        ]
        return choice(adjective_options)
        


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
