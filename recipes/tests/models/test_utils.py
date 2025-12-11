from django.test import TestCase
from recipes.models import User
from recipes.tests.utils import (
    create_test_user,
    create_test_users,
    create_test_recipe,
    create_test_recipes,
    create_test_form_data,
    create_test_image,
    create_invalid_image,
    get_default_user,
)


class TestUtilsTests(TestCase):
    """
    Test utility functions.
    """

    def test_create_test_user(self):
        """Test creating a single user."""
        user = create_test_user(username="@testuser")
        self.assertEqual(user.username, "@testuser")
        self.assertEqual(user.first_name, "Test")

    def test_create_test_user_with_defaults(self):
        """Test creating user with auto-generated username."""
        user = create_test_user()
        self.assertTrue(user.username.startswith("@testuser_"))

    def test_create_test_user_with_custom_fields(self):
        """Test creating user with custom fields."""
        user = create_test_user(
            username="@custom",
            first_name="Custom",
            last_name="Name",
            email="custom@test.com",
        )
        self.assertEqual(user.first_name, "Custom")
        self.assertEqual(user.last_name, "Name")
        self.assertEqual(user.email, "custom@test.com")

    def test_create_test_users(self):
        """Test creating multiple users."""
        users = create_test_users(count=3)
        self.assertEqual(len(users), 3)
        self.assertEqual(users[0].username, "@testuser0")

    def test_create_test_users_with_custom_fields(self):
        """Test creating users with custom first and last names."""
        users = create_test_users(
            count=2, username="custom", first_name="Custom", last_name="User"
        )
        self.assertEqual(len(users), 2)
        # First user should use kwargs.get('first_name', f'Test{i}') which will be 'Custom' from kwargs
        self.assertEqual(users[0].last_name, "User")

    def test_create_test_recipe(self):
        """Test creating a recipe."""
        recipe = create_test_recipe()
        self.assertEqual(recipe.title, "Test Recipe")
        self.assertIsNotNone(recipe.author)

    def test_create_test_recipe_with_existing_johndoe(self):
        """Test creating recipe when @johndoe already exists."""
        User.objects.create_user(
            username="@johndoe", email="johndoe@test.com", password="Password123"
        )
        recipe = create_test_recipe()
        self.assertEqual(recipe.author.username, "@johndoe")

    def test_create_test_recipe_with_custom_author(self):
        """Test creating recipe with specific author."""
        author = create_test_user(username="@author")
        recipe = create_test_recipe(author=author)
        self.assertEqual(recipe.author, author)

    def test_create_test_recipes(self):
        """Test creating multiple recipes."""
        recipes = create_test_recipes(count=3)
        self.assertEqual(len(recipes), 3)
        self.assertEqual(recipes[0].title, "Test Recipe 1")

    def test_create_test_recipes_with_custom_title(self):
        """Test creating recipes with custom title."""
        recipes = create_test_recipes(count=2, title="Custom Recipe")
        self.assertEqual(recipes[0].title, "Custom Recipe")
        self.assertEqual(recipes[1].title, "Custom Recipe")

    def test_create_test_form_data(self):
        """Test creating form data."""
        data = create_test_form_data()
        self.assertEqual(data["title"], "Test Recipe")
        self.assertEqual(data["servings"], 4)

    def test_create_test_form_data_with_overrides(self):
        """Test creating form data with custom values."""
        data = create_test_form_data(title="Custom", servings=8)
        self.assertEqual(data["title"], "Custom")
        self.assertEqual(data["servings"], 8)

    def test_create_test_image(self):
        """Test creating a test image."""
        image = create_test_image()
        self.assertEqual(image.name, "test.jpg")
        self.assertEqual(image.content_type, "image/jpeg")

    def test_create_test_image_custom(self):
        """Test creating custom test image."""
        image = create_test_image(name="custom.png", size=(200, 200), format="PNG")
        self.assertEqual(image.name, "custom.png")
        self.assertEqual(image.content_type, "image/png")

    def test_create_test_image_non_jpeg_format(self):
        """Test creating image with non-JPEG format."""
        image = create_test_image(format="GIF")
        self.assertEqual(image.content_type, "image/gif")

    def test_create_invalid_image(self):
        """Test creating an invalid image file."""
        invalid = create_invalid_image()
        self.assertEqual(invalid.name, "invalid.txt")
        self.assertEqual(invalid.content_type, "text/plain")
        self.assertEqual(invalid.read(), b"This is not an image")

    def test_create_invalid_image_custom_name(self):
        """Test creating invalid image with custom name."""
        invalid = create_invalid_image(name="fake.jpg")
        self.assertEqual(invalid.name, "fake.jpg")
        self.assertEqual(invalid.content_type, "text/plain")

    def test_get_default_user(self):
        """Test getting default user from fixture."""
        User.objects.create_user(
            username="@johndoe", email="johndoe@test.com", password="Password123"
        )
        user = get_default_user()
        self.assertEqual(user.username, "@johndoe")
