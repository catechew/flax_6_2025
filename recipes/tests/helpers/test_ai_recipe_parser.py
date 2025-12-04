from django.test import TestCase
from recipes.helpers.ai_recipe_parser import (
    parse_time_string,
    extract_hours,
    extract_minutes,
    format_ingredients_for_form,
    format_single_ingredient,
    parse_ai_recipe_data,
    map_ai_dietary_tags,
    get_dietary_tag_mapping,
)


class ParseTimeStringTests(TestCase):
    """Test time string parsing."""

    def test_parse_empty_string(self):
        """Test empty string returns 0."""
        self.assertEqual(parse_time_string(''), 0)
        self.assertEqual(parse_time_string(None), 0)

    def test_parse_minutes_only(self):
        """Test parsing minutes only."""
        self.assertEqual(parse_time_string('15 minutes'), 15)
        self.assertEqual(parse_time_string('30 min'), 30)

    def test_parse_hours_only(self):
        """Test parsing hours only."""
        self.assertEqual(parse_time_string('1 hour'), 60)
        self.assertEqual(parse_time_string('2 hours'), 120)

    def test_parse_hours_and_minutes(self):
        """Test parsing combined time."""
        self.assertEqual(parse_time_string('1 hour 30 minutes'), 90)
        self.assertEqual(parse_time_string('2 hours 45 min'), 165)


class ExtractHoursTests(TestCase):
    """Test hour extraction."""

    def test_no_hours(self):
        """Test string with no hours."""
        self.assertEqual(extract_hours('30 minutes'), 0)

    def test_one_hour(self):
        """Test single hour."""
        self.assertEqual(extract_hours('1 hour'), 1)

    def test_multiple_hours(self):
        """Test multiple hours."""
        self.assertEqual(extract_hours('3 hours'), 3)


class ExtractMinutesTests(TestCase):
    """Test minute extraction."""

    def test_no_minutes(self):
        """Test string with no minutes."""
        self.assertEqual(extract_minutes('1 hour'), 0)

    def test_minutes_only(self):
        """Test minutes only."""
        self.assertEqual(extract_minutes('45 minutes'), 45)

    def test_combined_time(self):
        """Test extracting minutes from combined time."""
        self.assertEqual(extract_minutes('1 hour 30 minutes'), 30)


class FormatIngredientsTests(TestCase):
    """Test ingredient formatting."""

    def test_format_with_weight(self):
        """Test formatting ingredient with weight."""
        ingredients = ['400g spaghetti']
        result = format_ingredients_for_form(ingredients)
        self.assertEqual(result, 'Spaghetti (400g)')

    def test_format_with_volume(self):
        """Test formatting ingredient with volume."""
        ingredients = ['100ml olive oil']
        result = format_ingredients_for_form(ingredients)
        self.assertEqual(result, 'Olive oil (100ml)')

    def test_format_with_count(self):
        """Test formatting ingredient with count."""
        ingredients = ['2 cloves garlic']
        result = format_ingredients_for_form(ingredients)
        self.assertEqual(result, 'Garlic (2 cloves)')

    def test_format_multiple_ingredients(self):
        """Test formatting multiple ingredients."""
        ingredients = ['400g pasta', '2 cloves garlic']
        result = format_ingredients_for_form(ingredients)
        self.assertIn('Pasta (400g)', result)
        self.assertIn('Garlic (2 cloves)', result)

    def test_format_to_taste(self):
        """Test formatting 'to taste' ingredients."""
        ingredients = ['Salt to taste']
        result = format_ingredients_for_form(ingredients)
        self.assertEqual(result, 'Salt to taste (as needed)')


class ParseAIRecipeDataTests(TestCase):
    """Test parsing complete AI recipe data."""

    def test_parse_complete_recipe(self):
        """Test parsing complete recipe data."""
        ai_data = {
            'title': 'Test Recipe',
            'ingredients': ['400g pasta', '2 cloves garlic'],
            'steps': ['Boil water', 'Cook pasta'],
            'prep_time': '15 minutes',
            'cook_time': '1 hour 30 minutes',
            'servings': 4,
            'dietary_info': ['vegetarian'],
            'description': 'A test recipe',
        }

        result = parse_ai_recipe_data(ai_data)

        self.assertEqual(result['title'], 'Test Recipe')
        self.assertEqual(result['prep_time_hours'], 0)
        self.assertEqual(result['prep_time_minutes'], 15)
        self.assertEqual(result['cook_time_hours'], 1)
        self.assertEqual(result['cook_time_minutes'], 30)
        self.assertEqual(result['servings'], 4)
        self.assertIn('Pasta (400g)', result['ingredients'])


class DietaryTagMappingTests(TestCase):
    """Test dietary tag mapping."""

    def test_get_mapping(self):
        """Test getting dietary mapping."""
        mapping = get_dietary_tag_mapping()
        self.assertIn('vegetarian', mapping)
        self.assertEqual(mapping['vegetarian'], 'Vegetarian')

    def test_map_tags(self):
        """Test mapping AI tags to system tags."""
        ai_tags = ['vegetarian', 'vegan', 'gluten-free']
        result = map_ai_dietary_tags(ai_tags)

        self.assertIn('Vegetarian', result)
        self.assertIn('Vegan', result)
        self.assertIn('Gluten-Free', result)

    def test_map_unknown_tags(self):
        """Test mapping unknown tags."""
        ai_tags = ['unknown-diet']
        result = map_ai_dietary_tags(ai_tags)
        self.assertEqual(len(result), 0)