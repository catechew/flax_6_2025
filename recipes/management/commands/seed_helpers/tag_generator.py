""" Tag generation for recipe seeding. """

from random import randint, sample

TAG_OPTIONS = {
    'course': ['dessert', 'main', 'appetiser', 'breakfast', 'snack'],
    
    'cuisine': [
        'Japanese', 'Italian', 'Chinese', 'Asian', 'Persian',
        'Jamaican', 'Western', 'British', 'Lebanese', 'Middle-Eastern'
    ],
    
    'dietary': [
        'vegetarian', 'vegan', 'halal', 'kosher',
        'gluten-free', 'dairy-free'
    ],
    
    'other': [
        'high protein', 'low calorie', 'low carb', 'quick', 'budget',
        'quick easy', 'budget-friendly', 'cheap', 'simple', 'viral trendy',
        'instagram worthy aesthetic', '5-minute', 'one pot',
        'leftover-friendly', 'meal-prep batch', 'protein-packed filling',
        'vegetarian healthy', 'vegan plant based', 'late-night comfort',
        'study snack energy', 'cozy', 'freezer friendly',
        'restaurant style fancy', 'homemade', 'spicy', 'creamy', 'crispy',
        'trending', 'tiktok famous', 'brunch-worthy special',
        'microwave easy', 'dorm room friendly', 'high protein low calories',
        'italian', 'indian', 'vietnamese', 'chinese takeout',
        'mediterranean', 'summer', 'gourmet', 'weekend treat', 'midweek'
    ]
}

class TagGenerator:
    """ Generates random tags for recipes. """

    @staticmethod
    def generate_tags(tag_type):
        """
        Generate random tags of specified type.

        Args:
            tag_type: One of 'course', 'cuisine', 'dietary', 'other'

        Returns:
            Comma-separated tags or empty string
        """
        options = TAG_OPTIONS.get(tag_type, [])
        num_tags = randint(0, 2)
        if num_tags == 0:
            return ''
        selected = sample(options, num_tags)
        return ','.join(selected)