""" 
Management command to seed the database with demo data. 
"""

from random import choice
from django.core.management.base import BaseCommand
from recipes.models import User, Recipe
from .seed_helpers import (
    RecipeDataGenerator,
    TagGenerator,
    ImageHandler,
)
from .seed_helpers.user_data import (
    create_random_user_payload,
    create_fixture_user_payload,
)

USER_FIXTURES = [
    {
        "username": "@johndoe",
        "email": "john.doe@example.org",
        "first_name": "John",
        "last_name": "Doe",
        "is_admin": True,
    },
    {
        "username": "@janedoe",
        "email": "jane.doe@example.org",
        "first_name": "Jane",
        "last_name": "Doe",
    },
    {
        "username": "@charlie",
        "email": "charlie.johnson@example.org",
        "first_name": "Charlie",
        "last_name": "Johnson",
    },
]

class Command(BaseCommand):
    """ Seed database with users and recipes. """

    USER_COUNT = 200
    RECIPE_COUNT = 500
    DEFAULT_PASSWORD = 'Password123'
    help = "Seeds the database with sample data"

    def handle(self, *args, **options):
        """ Execute seeding workflow. """
        self._seed_users()
        self._seed_recipes()

    def _seed_users(self):
        """ Create fixture and random users. """
        self._create_fixture_users()
        self._create_random_users()

    def _create_fixture_users(self):
        """ Create predefined fixture users. """
        for user_data in USER_FIXTURES:
            if user_data['username'] == '@johndoe':
                self._create_admin_user(user_data)
            else:
                self._try_create_user(user_data)

    def _create_admin_user(self, user_data):
        """ Create admin superuser. """
        try:
            user = User.objects.create_superuser(
                username=user_data['username'],
                email=user_data['email'],
                password=self.DEFAULT_PASSWORD,
                first_name=user_data['first_name'],
                last_name=user_data['last_name']
            )
            user.is_staff = True
            user.save()
        except Exception:
            pass

    def _create_random_users(self):
        """ Generate random users until target count reached. """
        while User.objects.count() < self.USER_COUNT:
            count = User.objects.count()
            print(f"Seeding user {count}/{self.USER_COUNT}", end='\r')
            self._generate_user()
        print("User seeding complete.      ")

    def _generate_user(self):
        """ Generate single random user. """
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        user_data = {
            'username': _create_username(first_name, last_name),
            'email': _create_email(first_name, last_name),
            'first_name': first_name,
            'last_name': last_name
        }
        self._try_create_user(user_data)

    def _try_create_user(self, user_data):
        """ Attempt user creation, ignore failures. """
        try:
            User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=self.DEFAULT_PASSWORD,
                first_name=user_data['first_name'],
                last_name=user_data['last_name']
            )
        except Exception:
            pass

    def _seed_recipes(self):
        """ Generate recipes up to target count. """
        users = list(User.objects.all())
        if not users:
            print("No users found. Cannot create recipes.")
            return

        while Recipe.objects.count() < self.RECIPE_COUNT:
            count = Recipe.objects.count()
            print(f"Seeding recipe {count}/{self.RECIPE_COUNT}", end='\r')
            self._generate_recipe(users)
        print("Recipe seeding complete.")

    def _generate_recipe(self, users):
        """ Generate single random recipe. """
        title = RecipeDataGenerator.generate_title()
        prep_hours, prep_mins = RecipeDataGenerator.generate_time_component()
        cook_hours, cook_mins = RecipeDataGenerator.generate_time_component()
        image_content, image_filename = ImageHandler.load_image(title)

        recipe_data = {
            'title': title,
            'author': choice(users),
            'publication_date': RecipeDataGenerator.generate_date(),
            'ingredients': RecipeDataGenerator.generate_ingredients(),
            'steps': RecipeDataGenerator.generate_steps(),
            'prep_time_hours': prep_hours,
            'prep_time_minutes': prep_mins,
            'cook_time_hours': cook_hours,
            'cook_time_minutes': cook_mins,
            'course_tags': TagGenerator.generate_tags('course'),
            'cuisine_tags': TagGenerator.generate_tags('cuisine'),
            'dietary_tags': TagGenerator.generate_tags('dietary'),
            'other_tags': TagGenerator.generate_tags('other'),
            'image_content': image_content,
            'image_filename': image_filename
        }
        self._try_create_recipe(recipe_data)

    def _try_create_recipe(self, data):
        """ Attempt recipe creation, ignore failures. """
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
                other_tags=data['other_tags']
            )
            if data['image_content'] and data['image_filename']:
                recipe.image.save(
                    data['image_filename'],
                    data['image_content'],
                    save=True
                )
        except Exception as e:
            print(f"Error creating recipe: {e}")

def _create_username(first_name, last_name):
    """ Create username from first and last names. """
    return f"@{first_name.lower()}{last_name.lower()}"

def _create_email(first_name, last_name):
    """ Create email from first and last names. """
    return f"{first_name}.{last_name}@example.org"