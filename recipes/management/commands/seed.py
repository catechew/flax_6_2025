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

    def _seed_fixture_users(self):
        for data in USER_FIXTURES:
            payload = create_fixture_user_payload(data)
            self._create_user(payload)

    def _seed_random_users(self):
        """ Generate random users until target count reached. """
        while User.objects.count() < self.USER_COUNT:
            self._create_user(create_random_user_payload())
        self.stdout.write(self.style.SUCCESS("User seeding complete"))

    def _create_user(self, data):
        try:
            creator = (
                User.objects.create_superuser
                if data["is_admin"]
                else User.objects.create_user
            )
            creator(
                username=data["username"],
                email=data["email"],
                password=self.DEFAULT_PASSWORD,
                first_name=data["first_name"],
                last_name=data["last_name"],
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

    def _create_recipe(self, users):
        title = RecipeDataGenerator.generate_title()
        prep_hours, prep_mins = RecipeDataGenerator.generate_time_component()
        cook_hours, cook_mins = RecipeDataGenerator.generate_time_component()
        image, filename = ImageHandler.load_image(title)

        try:
            recipe = Recipe.objects.create(
                title=title,
                author=choice(users),
                publication_date=RecipeDataGenerator.generate_date(),
                ingredients=RecipeDataGenerator.generate_ingredients(),
                steps=RecipeDataGenerator.generate_steps(),
                prep_time_hours=prep_hours,
                prep_time_minutes=prep_mins,
                cook_time_hours=cook_hours,
                cook_time_minutes=cook_mins,
                course_tags=TagGenerator.generate_tags("course"),
                cuisine_tags=TagGenerator.generate_tags("cuisine"),
                dietary_tags=TagGenerator.generate_tags("dietary"),
                other_tags=TagGenerator.generate_tags("other"),
            )
            self._attach_image(recipe, image, filename)
        except Exception:
            pass

    @staticmethod
    def _attach_image(recipe, content, filename):
        if content and filename:
            recipe.image.save(filename, content, save=True)