import os
from random import randint
from django.conf import settings
from django.core.files.base import ContentFile

"""
Image handling for recipe seeding.
"""

DISH_TYPE_MAPPING = {
    "pasta": ["pasta", "spaghetti", "bolognese", "pasta bake"],
    "pesto": ["pesto pasta"],
    "mac-and-cheese": ["macaroni", "penne", "baked four cheese mac"],
    "risotto": ["risotto"],
    "ramen": [
        "ramen",
        "mee goreng",
        "buldak",
        "instant noodles",
        "cup noodles",
        "noodle",
        "pot noodle",
    ],
    "pad-thai": [
        "pad thai",
    ],
    "rice": [
        "rice",
        "fried rice",
        "rice bowl",
        "egg fried rice",
        "microwave rice",
        "nasi lemak",
    ],
    "katsu": ["katsu", "japanese curry"],
    "curry": ["curry", "thai curry", "chickpea curry", "aloo gobi", "dal", "tarka"],
    "butter-chicken": ["butter chicken"],
    "soup": ["pho", "gyoza", "chicken noodle soup", "lemongrass soup"],
    "tomato-soup": ["tomato soup"],
    "pizza": ["pizza"],
    "toast": ["toast", "chilli cheese toast"],
    "burger": ["burger", "cheeseburger"],
    "chips": ["oven chips"],
    "potato-wedges": ["potato wedges", "garlic butter wedges"],
    "fish-and-chips": [
        "fish and chips",
        "british fish and chips",
        "cod & chips",
        "sea bass with wedges",
    ],
    "wrap": ["wrap", "quesadilla", "fajitas"],
    "salad": ["salad"],
    "acai": ["acai bowl", "acai", "breakfast parfait"],
    "stir-fry": ["stir fry", "stir-fry"],
    "dessert": [
        "cake",
        "mug cake",
        "chocolate banana jar cake",
        "double chocolate parfait",
    ],
    "cheesecake": ["cheesecake"],
    "tanghulu": ["tanghulu"],
    "apple-pie": ["apple pie"],
    "banana-split": ["banana split"],
    "oats": ["overnight oats", "cereal snack"],
    "drink": [
        "smoothie",
        "very berry hibiscus refresher",
        "raspberry coconut cooler",
        "raspberry ripple milkshake",
    ],
    "bubble-tea": ["bubble tea", "brown sugar boba"],
    "iced-drink": [
        "sweet iced tea",
        "iced tea",
        "peach mocktail",
        "strawberry lemonade",
    ],
    "detox-water": ["detox water", "summer berries cooler"],
    "matcha": ["matcha", "vanilla matcha"],
    "coffee": [
        "latte",
        "macchiato",
        "mocha",
        "frappé",
        "frappe",
        "coffee",
        "cappuccino",
    ],
    "hot-choc": ["hot chocolate"],
    "side": ["mashed", "pub style mash"],
    "baked-beans": ["baked beans"],
    "hummus": ["hummus"],
}


class ImageHandler:
    """
    Handles recipe image loading.
    """

    @staticmethod
    def get_dish_type(title):
        """Map recipe title to dish type."""
        title_lower = title.lower()
        matches = [
            dish_type
            for dish_type, keywords in DISH_TYPE_MAPPING.items()
            if any(keyword in title_lower for keyword in keywords)
        ]
        return matches[0] if matches else "default"

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
        """Load image file from static directory."""
        image_path = f"static/images/food_placeholders/{dish_type}.jpg"
        full_path = os.path.join(settings.BASE_DIR, image_path)
        if os.path.exists(full_path):
            return ImageHandler._create_image_content(full_path, dish_type)
        return ImageHandler._load_default_image()

    @staticmethod
    def _create_image_content(path, dish_type):
        """Create ContentFile from image path."""
        with open(path, "rb") as f:
            content = ContentFile(f.read())
            filename = f"recipe_{dish_type}_{randint(1000, 9999)}.jpg"
            return content, filename

    @staticmethod
    def _load_default_image():
        """Load default placeholder image."""
        default_path = os.path.join(
            settings.BASE_DIR, "static/images/food_placeholders/default.jpg"
        )
        if os.path.exists(default_path):
            return ImageHandler._create_image_content(default_path, "default")
        return None, None
