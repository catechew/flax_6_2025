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
    find_last_digit,
)

class ParseTimeStringTests(TestCase):
    """
    Test time string parsing.
    """

    def test_parse_empty_string(self):
        """ Test empty string returns 0. """
        self.assertEqual(parse_time_string(''), 0)
        self.assertEqual(parse_time_string(None), 0)

    def test_parse_minutes_only(self):
        """ Test parsing minutes only. """
        self.assertEqual(parse_time_string('15 minutes'), 15)
        self.assertEqual(parse_time_string('30 min'), 30)

    def test_parse_hours_only(self):
        """ Test parsing hours only. """
        self.assertEqual(parse_time_string('1 hour'), 60)
        self.assertEqual(parse_time_string('2 hours'), 120)

    def test_parse_hours_and_minutes(self):
        """ Test parsing combined time. """
        self.assertEqual(parse_time_string('1 hour 30 minutes'), 90)
        self.assertEqual(parse_time_string('2 hours 45 min'), 165)


class ExtractHoursTests(TestCase):
    """
    Test hour extraction.
    """

    def test_no_hours(self):
        """ Test string with no hours. """
        self.assertEqual(extract_hours('30 minutes'), 0)

    def test_one_hour(self):
        """ Test single hour. """
        self.assertEqual(extract_hours('1 hour'), 1)

    def test_multiple_hours(self):
        """ Test multiple hours. """
        self.assertEqual(extract_hours('3 hours'), 3)

    def test_extract_hours_with_invalid_format(self):
        """ Test extract_hours handles invalid format gracefully. """
        result = extract_hours('invalid hour format')
        self.assertEqual(result, 0)

    def test_extract_hours_with_only_hour_keyword(self):
        """ Test extract_hours with just 'hour' keyword (empty parts). """
        result = extract_hours('hour')
        self.assertEqual(result, 0)

    def test_extract_hours_with_non_numeric(self):
        """ Test extract_hours with non-numeric value before hour. """
        result = extract_hours('abc hour')
        self.assertEqual(result, 0)


class ExtractMinutesTests(TestCase):
    """
    Test minute extraction.
    """

    def test_no_minutes(self):
        """ Test string with no minutes. """
        self.assertEqual(extract_minutes('1 hour'), 0)

    def test_minutes_only(self):
        """ Test minutes only. """
        self.assertEqual(extract_minutes('45 minutes'), 45)

    def test_combined_time(self):
        """ Test extracting minutes from combined time. """
        self.assertEqual(extract_minutes('1 hour 30 minutes'), 30)

    def test_extract_minutes_with_invalid_format(self):
        """ Test extract_minutes handles invalid format gracefully. """
        result = extract_minutes('invalid min format')
        self.assertEqual(result, 0)

    def test_extract_minutes_with_only_min_keyword(self):
        """ Test extract_minutes with just 'min' keyword (empty parts). """
        result = extract_minutes('min')
        self.assertEqual(result, 0)

    def test_extract_minutes_with_non_numeric(self):
        """ Test extract_minutes with non-numeric value before min. """
        result = extract_minutes('xyz min')
        self.assertEqual(result, 0)


class FormatIngredientsTests(TestCase):
    """
    Test ingredient formatting. 
    """

    def test_format_with_weight(self):
        """ Test formatting ingredient with weight. """
        ingredients = ['400g spaghetti']
        result = format_ingredients_for_form(ingredients)
        self.assertEqual(result, 'Spaghetti (400g)')

    def test_format_with_volume(self):
        ingredients = ['100ml olive oil']
        result = format_ingredients_for_form(ingredients)
        self.assertEqual(result, 'Olive oil (100ml)')

    def test_format_with_count(self):
        ingredients = ['2 cloves garlic']
        result = format_ingredients_for_form(ingredients)
        self.assertEqual(result, 'Garlic (2 cloves)')

    def test_format_multiple_ingredients(self):
        """ Test formatting multiple ingredients. """
        ingredients = ['400g pasta', '2 cloves garlic']
        result = format_ingredients_for_form(ingredients)
        self.assertIn('Pasta (400g)', result)
        self.assertIn('Garlic (2 cloves)', result)

    def test_format_to_taste(self):
        """ Test formatting 'to taste' ingredients. """
        ingredients = ['Salt to taste']
        result = format_ingredients_for_form(ingredients)
        self.assertEqual(result, 'Salt to taste (as needed)')

    def test_find_last_digit_with_no_digits(self):
        """ Test find_last_digit returns 0 when no digits found. """
        result = find_last_digit(['no', 'digits', 'here'])
        self.assertEqual(result, 0)

    def test_format_empty_ingredient_list(self):
        """ Test formatting empty ingredient list. """
        result = format_ingredients_for_form([])
        self.assertEqual(result, '')

    def test_format_ingredient_with_whitespace(self):
        """ Test formatting ingredient with extra whitespace. """
        result = format_ingredients_for_form(['  400g pasta  '])
        self.assertEqual(result, 'Pasta (400g)')

    def test_format_ingredients_with_empty_strings(self):
        """ Test formatting with empty strings (covers line 51-52). """
        ingredients = ['400g pasta', '   ', '', '2 eggs', '\t', '\n']
        result = format_ingredients_for_form(ingredients)

        # Should only have 2 lines (pasta and eggs)
        lines = [line for line in result.split('\n') if line.strip()]
        self.assertEqual(len(lines), 2)
        self.assertIn('Pasta (400g)', result)
        self.assertIn('Eggs (2)', result)

    def test_format_ingredients_only_whitespace(self):
        """ Test formatting with only whitespace ingredients. """
        ingredients = ['  ', '\t', '\n', '   ']
        result = format_ingredients_for_form(ingredients)
        self.assertEqual(result, '')

    def test_format_ingredients_mixed_empty_and_valid(self):
        """ Test formatting with mix of empty and valid. """
        ingredients = ['', '400g flour', '  ', '2 cups sugar', '\t\n', '1 tsp salt']
        result = format_ingredients_for_form(ingredients)

        lines = result.split('\n')
        # Should have exactly 3 ingredients
        self.assertEqual(len(lines), 3)
        self.assertIn('Flour (400g)', result)
        self.assertIn('Sugar (2 cups)', result)
        self.assertIn('Salt (1 tsp)', result)


class ParseAIRecipeDataTests(TestCase):
    """
    Test parsing complete AI recipe data.
    """

    def test_parse_complete_recipe(self):
        """ Test parsing complete recipe data. """
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
    """
    Test dietary tag mapping.
    """

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