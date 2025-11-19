from django.core.management.base import BaseCommand, CommandError
from recipes.models import User, Recipe

class Command(BaseCommand):
    """
    Management command to remove (unseed) user data from the database.

    This command deletes all non-staff users from the database. It is designed
    to complement the corresponding "seed" command, allowing developers to
    reset the database to a clean state without removing administrative users.

    Attributes:
        help (str): Short description displayed when running
            `python manage.py help unseed`.
    """
    
    help = 'Removes all non-admin seeded users from the database.'

    def handle(self, *args, **options):
        """Start the unseeding process"""

        # Delete all recipes.
        recipe_count = Recipe.objects.count()
        Recipe.objects.all().delete()
        print(f"Deleted {recipe_count} recipes")

        # Delete all non-staff users preserving admin accounts.
        user_count = User.objects.filter(is_staff=False).count()
        User.objects.filter(is_staff=False, is_superuser=False).delete()
        print(f"Deleted {user_count} users")
        print("Unseeding complete")

