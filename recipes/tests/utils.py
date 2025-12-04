"""
Utility functions for creating test data in tests
"""

from django.contrib.auth import get_user_model
from django.utils import timezone
from recipes.models import Recipe
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from io import BytesIO
import uuid


User = get_user_model()

def create_test_user(username=None, password='Password123', **kwargs):
    """
    Create test user with default values.

    username: Username (default: @testuser)
    password: Password (default: Password123)
    **kwargs: Additional user fields to override

    returns user instance
    """

    if username is None:
        username = f'@testuser_{uuid.uuid4().hex[:8]}'

    defaults = {
        'first_name':'Test',
        'last_name': 'User',
        'email': f'{username.strip("@")}@test.com'
    }

    defaults.update(kwargs)

    return User.objects.create_user(
        username=username,
        password=password,
        **defaults
    )

def create_test_users(count=1, username='testuser', **kwargs):
    """
    Create multiple test users 

    count: number of users to create
    username: prefix for username (default '@testuser')
    **kwargs: Additional fields to set on all users

    returns llist of created user instances
    """
    users = []
    for i in range(count):
        user = create_test_user(
            username = f'@{username}{i}',
            first_name = kwargs.get('first_name', f'Test{i}'),
            last_name = kwargs.get('last_name', 'User'),
            **{k: v for k, v in kwargs.items() if k not in ['first_name', 'last_name']}
        )
        users.append(user)
    return users

def create_test_recipe(author=None, **kwargs):
    """
    Create a test recipe with default values.

    author: Recipe author (default: creates new user @johndoe)
    **kwargs: Recipe fields to override

    Returns recipe instance
    """

    if author is None:
        try:
            author = User.objects.get(username='@johndoe')
        except User.DoesNotExist:
            author = create_test_user(username='@johndoe')
    
    defaults = {
        'title': 'Test Recipe',
        'publication_date': timezone.now().date(),
        'ingredients': 'test ingredient (1 cup)',
        'steps': 'test step 1',
        'servings': 4
    }
    defaults.update(kwargs)

    return Recipe.objects.create(author=author, **defaults)

def create_test_recipes(count=3, author=None, **kwargs):
    """
    Create multiple test recipes.
    
    Returns list of recipe instances.
    """
    recipes = []
    for i in range(1, count + 1):
        recipe_kwargs = kwargs.copy()
        recipe_kwargs['title'] = recipe_kwargs.get('title', f'Test Recipe {i}')
        recipes.append(create_test_recipe(author=author, **recipe_kwargs))
    return recipes

def create_test_form_data(**kwargs):
    """
    Create form data dictionary for RecipeForm.
    
    Returns dictionary of form data
    """

    defaults = {
        'title': 'Test Recipe',
        'publication_date': timezone.now().date(),
        'ingredients': 'test ingredient (1 cup)',
        'steps': 'test step 1',
        'servings': 4,
        'prep_time_hours': 0,
        'prep_time_minutes': 30,
        'cook_time_hours': 1,
        'cook_time_minutes': 0,
        'private' : False,
    }
    defaults.update(kwargs)
    return defaults

def create_test_image(name='test.jpg', size=(100,100), color='red', format='JPEG'):
    """
    Create a test image file for upload testing
    name: Filename (default: test.jpg)
    size: Image dimensions tuple (default: (100,100))
    color: Image color (default:red)
    format: Image format (default: JPEG)
    
    Returns SimpleUploadedFile instance
    """

    image = Image.new('RGB', size, color=color)
    image_file = BytesIO()
    image.save(image_file, format)
    image_file.seek(0)

    content_type = 'image/jpeg' if format == 'JPEG' else f'image/{format.lower()}'

    return SimpleUploadedFile(
        name=name,
        content=image_file.read(),
        content_type=content_type,
    )

def create_invalid_image(name='invalid.txt'):
    """
    Create an invalid image file (text file).
    name: Filename (default: invalid.txt)
    
    Returns SimpleUploadedFile instance
    """

    return SimpleUploadedFile(
        name=name,
        content=b'This is not an image',
        content_type='text/plain'    
    )

def get_default_user():
    """
    Get the defaul test user (@johndoe) from fixture.
    
    Returns user instance
    """

    return User.objects.get(username='@johndoe')


    



