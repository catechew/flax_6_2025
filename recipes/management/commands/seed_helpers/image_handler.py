""" Image handling for recipe seeding. """

import os
from random import randint
from django.conf import settings
from django.core.files.base import ContentFile

DISH_TYPE_MAPPING = {
    'pasta': ['pasta', 'spaghetti', 'macaroni', 'bolognese', 'penne', 'pasta bake', 
              'ramen', 'noodles', 'mee goreng'],

    'rice': ['rice', 'fried rice', 'rice bowl', 'egg fried rice', 'microwave rice', 'nasi lemak'],

    'curry': ['curry', 'butter chicken', 'tofu thai curry', 'mushroom curry', 'chickpea curry', 'aloo gobi',
              'katsu', 'dal', 'tarka'],

    'soup': ['soup', 'tomato soup', 'pho', 'gyoza soup'],

    'pizza': ['pizza', 'margherita', 'frozen pizza', 'pizza toast'],

    'burger': ['burger', 'cheeseburger', 'fish and chips'],

    'wrap': ['wrap', 'quesadilla', 'fajitas'],

    'salad': ['salad', 'caesar salad', 'acai bowl', 'breakfast parfait', 'stir-fry'],

    'toast': ['toast', 'beans on toast', 'chilli cheese toast'],

    'dessert': ['dessert', 'cake', 'mug cake', 'muffins', 'banana split', "s'mores", 
                'apple pie', 'tanghulu'],

    'drink': ['smoothie', 'milkshake', 'latte', 'hot chocolate',  'matcha', 
              'mocktail', 'bubble tea', 'frappé', 'detox water'],
}

class ImageHandler:
    """ Handles recipe image loading. """

    @staticmethod
    def get_dish_type(title):
        """ Map recipe title to dish type. """
        title_lower = title.lower()
        for dish_type, keywords in DISH_TYPE_MAPPING.items():
            for keyword in keywords:
                if keyword in title_lower:
                    return dish_type
        return 'default'

    @staticmethod
    def load_image(title):
        """
        Load placeholder image based on recipe title.

        Args:
            title: Recipe title

        Returns:
            Tuple of (ContentFile, filename) or (None, None)
        """
        try:
            dish_type = ImageHandler.get_dish_type(title)
            return ImageHandler._load_image_file(dish_type)
        except Exception as e:
            print(f"Error loading placeholder image: {e}")
            return None, None

    @staticmethod
    def _load_image_file(dish_type):
        """ Load image file from static directory. """
        image_path = f'static/images/food_placeholders/{dish_type}.jpg'
        full_path = os.path.join(settings.BASE_DIR, image_path)

        if os.path.exists(full_path):
            return ImageHandler._create_image_content(full_path, dish_type)

        return ImageHandler._load_default_image()

    @staticmethod
    def _create_image_content(path, dish_type):
        """ Create ContentFile from image path. """
        with open(path, 'rb') as f:
            content = ContentFile(f.read())
            filename = f"recipe_{dish_type}_{randint(1000, 9999)}.jpg"
            return content, filename

    @staticmethod
    def _load_default_image():
        """ Load default placeholder image. """
        default_path = os.path.join(
            settings.BASE_DIR,
            'static/images/food_placeholders/default.jpg'
        )
        if os.path.exists(default_path):
            return ImageHandler._create_image_content(default_path, 'default')
        return None, None