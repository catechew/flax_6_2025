""" 
Management command to remove seeded data from the database. 
"""


from django.core.management.base import BaseCommand
from recipes.models import User, Recipe


class Command(BaseCommand):
    """ Remove seeded users and recipes from database. """

    help = 'Removes all non-admin seeded users from the database.'

    def handle(self, *args, **options):
        """ Execute unseeding process. """
        self._delete_recipes()
        self._delete_users()
        self._print_success()

    def _delete_recipes(self):
        """ Delete all recipes from database. """
        recipe_count = Recipe.objects.count()
        Recipe.objects.all().delete()
        print(f"Deleted {recipe_count} recipes")

    def _delete_users(self):
        """ Delete non-staff users preserving admin accounts. """
        user_count = User.objects.filter(is_staff=False).count()
        User.objects.filter(is_staff=False, is_superuser=False).delete()
        self.stdout.write(
            self.style.SUCCESS(f"Deleted {user_count} users")
        )

    def _print_success(self):
        """ Print completion message. """
        self.stdout.write(self.style.SUCCESS("Unseeding complete"))