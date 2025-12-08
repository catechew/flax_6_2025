from django.test import TestCase, RequestFactory
from django.contrib.sessions.backends.db import SessionStore
from recipes.helpers.recipe_form_helpers import get_tag_action_from_request, check_category_for_tag_action, handle_tag_operation, get_tag_context, initialise_tag_session, get_tag_list_for_key, apply_tags_to_recipe, get_session_key, cleanup_session, apply_ai_dietary_tags, get_ai_prefill_from_session, store_ai_dietary_info
from recipes.models import User, Recipe
from datetime import date
from unittest.mock import patch, MagicMock


class GetTagActionFromRequestTests(TestCase):
    """
    Test get_tag_action_from_request function.
    """

    def setUp(self):
        """Set up test request factory."""
        self.factory = RequestFactory()

    def test_returns_none_for_get_request(self):
        """GET request returns None, None, None."""
        request = self.factory.get('/test/')
        result = get_tag_action_from_request(request)
        self.assertEqual(result, (None, None, None))

    def test_returns_add_action_for_course_tag(self):
        """POST with add_course_tag returns correct action."""
        request = self.factory.post('/test/', {'add_course_tag': 'breakfast'})
        result = get_tag_action_from_request(request)
        self.assertEqual(result, ('add', 'course', 'breakfast'))

    def test_returns_add_custom_action(self):
        """POST with custom tag returns correct action."""
        request = self.factory.post('/test/', {
            'add_course_tag_custom': '1',
            'course_tag_value': 'brunch'
        })
        result = get_tag_action_from_request(request)
        self.assertEqual(result, ('add', 'course', 'brunch'))

    def test_returns_remove_action(self):
        """POST with remove tag returns correct action."""
        request = self.factory.post('/test/', {'remove_dietary_tag': 'vegan'})
        result = get_tag_action_from_request(request)
        self.assertEqual(result, ('remove', 'dietary', 'vegan'))

    def test_returns_none_when_no_tag_action(self):
        """POST with no tag action returns None."""
        request = self.factory.post('/test/', {'other_field': 'value'})
        result = get_tag_action_from_request(request)
        self.assertEqual(result, (None, None, None))


class HandleTagOperationTests(TestCase):
    """
    Test handle_tag_operation function.
    """

    def setUp(self):
        """Set up session data."""
        self.session_data = {'course_tags': ['breakfast']}

    def test_add_new_tag(self):
        """Add new tag successfully."""
        result = handle_tag_operation(
            self.session_data, 'add', 'course', 'lunch'
        )
        self.assertTrue(result)
        self.assertIn('lunch', self.session_data['course_tags'])

    def test_add_duplicate_tag_returns_true(self):
        """Adding duplicate tag returns True (idempotent)."""
        result = handle_tag_operation(
            self.session_data, 'add', 'course', 'breakfast'
        )
        self.assertTrue(result)
        # Should only appear once
        self.assertEqual(
            self.session_data['course_tags'].count('breakfast'), 1
        )

    def test_remove_existing_tag(self):
        """Remove existing tag successfully."""
        result = handle_tag_operation(
            self.session_data, 'remove', 'course', 'breakfast'
        )
        self.assertTrue(result)
        self.assertNotIn('breakfast', self.session_data['course_tags'])

    def test_remove_nonexistent_tag_returns_false(self):
        """Removing non-existent tag returns False."""
        result = handle_tag_operation(
            self.session_data, 'remove', 'course', 'dinner'
        )
        self.assertFalse(result)

    def test_empty_value_returns_false(self):
        """Empty value returns False."""
        result = handle_tag_operation(
            self.session_data, 'add', 'course', ''
        )
        self.assertFalse(result)

    def test_whitespace_only_value_returns_false(self):
        """Whitespace-only value returns False."""
        result = handle_tag_operation(
            self.session_data, 'add', 'course', '   '
        )
        self.assertFalse(result)

    def test_value_too_long_returns_false(self):
        """Value longer than 50 characters returns False."""
        long_value = 'a' * 51
        result = handle_tag_operation(
            self.session_data, 'add', 'course', long_value
        )
        self.assertFalse(result)

    def test_value_exactly_50_chars_succeeds(self):
        """Value exactly 50 characters succeeds."""
        exact_value = 'a' * 50
        result = handle_tag_operation(
            self.session_data, 'add', 'course', exact_value
        )
        self.assertTrue(result)

    def test_none_action_returns_false(self):
        """None action returns False."""
        result = handle_tag_operation(
            self.session_data, None, 'course', 'lunch'
        )
        self.assertFalse(result)

    def test_none_category_returns_false(self):
        """None category returns False."""
        result = handle_tag_operation(
            self.session_data, 'add', None, 'lunch'
        )
        self.assertFalse(result)

    def test_none_value_returns_false(self):
        """None value returns False."""
        result = handle_tag_operation(
            self.session_data, 'add', 'course', None
        )
        self.assertFalse(result)

    def test_creates_tag_key_if_missing(self):
        """Creates tag key if it doesn't exist."""
        session = {}
        result = handle_tag_operation(session, 'add', 'dietary', 'vegan')
        self.assertTrue(result)
        self.assertIn('dietary_tags', session)
        self.assertIn('vegan', session['dietary_tags'])
        
    def test_invalid_action_returns_false(self):
        """Test handle_tag_operation returns False for invalid action."""
        session_data = {'course_tags': []}
        
        result = handle_tag_operation(
            session_data, 
            'invalid_action',  # ← Not "add" or "remove"
            'course', 
            'breakfast'
        )
        
        self.assertFalse(result)
        self.assertEqual(session_data['course_tags'], [])


class GetTagContextTests(TestCase):
    """
    Test get_tag_context function.
    """

    def test_returns_all_tag_categories(self):
        """Returns context with all tag categories."""
        session_data = {
            'course_tags': ['breakfast'],
            'dietary_tags': ['vegan'],
            'cuisine_tags': ['Italian'],
            'other_tags': ['quick'],
        }
        result = get_tag_context(session_data)

        self.assertEqual(result['course_tags'], ['breakfast'])
        self.assertEqual(result['dietary_tags'], ['vegan'])
        self.assertEqual(result['cuisine_tags'], ['Italian'])
        self.assertEqual(result['other_tags'], ['quick'])

        # Check options are present
        self.assertIn('course_options', result)
        self.assertIn('dietary_options', result)
        self.assertIn('cuisine_options', result)
        self.assertIn('other_options', result)

    def test_returns_empty_lists_when_no_tags(self):
        """Returns empty lists when tags not in session."""
        result = get_tag_context({})

        self.assertEqual(result['course_tags'], [])
        self.assertEqual(result['dietary_tags'], [])
        self.assertEqual(result['cuisine_tags'], [])
        self.assertEqual(result['other_tags'], [])


class InitialiseTagSessionTests(TestCase):
    """
    Test initialise_tag_session function.
    """

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='@testuser',
            email='test@example.com',
            password='Password123'
        )

        self.recipe = Recipe.objects.create(
            author=self.user,
            title='Test Recipe',
            publication_date=date.today(),
            ingredients='Test (1)',
            steps='Test step',
            course_tags='breakfast,lunch',
            dietary_tags='vegan',
            cuisine_tags='Italian',
            other_tags='quick',
        )

    def test_initialises_empty_tags_for_new_recipe(self):
        """Initialises empty tag lists for new recipe."""
        session_data = {}
        initialise_tag_session(session_data, recipe=None)

        self.assertEqual(session_data['course_tags'], [])
        self.assertEqual(session_data['dietary_tags'], [])
        self.assertEqual(session_data['cuisine_tags'], [])
        self.assertEqual(session_data['other_tags'], [])

    def test_initialises_tags_from_existing_recipe(self):
        """Initialises tags from existing recipe."""
        session_data = {}
        initialise_tag_session(session_data, recipe=self.recipe)

        self.assertIn('breakfast', session_data['course_tags'])
        self.assertIn('lunch', session_data['course_tags'])
        self.assertIn('vegan', session_data['dietary_tags'])
        self.assertIn('Italian', session_data['cuisine_tags'])
        self.assertIn('quick', session_data['other_tags'])


class ApplyTagsToRecipeTests(TestCase):
    """
    Test apply_tags_to_recipe function.
    """

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='@testuser',
            email='test@example.com',
            password='Password123'
        )

        self.recipe = Recipe.objects.create(
            author=self.user,
            title='Test Recipe',
            publication_date=date.today(),
            ingredients='Test (1)',
            steps='Test step',
        )

    def test_applies_tags_to_recipe(self):
        """Applies tags from session to recipe."""
        session_data = {
            'course_tags': ['breakfast', 'lunch'],
            'dietary_tags': ['vegan'],
            'cuisine_tags': ['Italian'],
            'other_tags': ['quick'],
        }

        apply_tags_to_recipe(self.recipe, session_data)

        self.assertEqual(self.recipe.course_tags, 'breakfast,lunch')
        self.assertEqual(self.recipe.dietary_tags, 'vegan')
        self.assertEqual(self.recipe.cuisine_tags, 'Italian')
        self.assertEqual(self.recipe.other_tags, 'quick')

    def test_handles_empty_tags(self):
        """Handles empty tag lists."""
        session_data = {
            'course_tags': [],
            'dietary_tags': [],
            'cuisine_tags': [],
            'other_tags': [],
        }

        apply_tags_to_recipe(self.recipe, session_data)

        self.assertEqual(self.recipe.course_tags, '')
        self.assertEqual(self.recipe.dietary_tags, '')
        self.assertEqual(self.recipe.cuisine_tags, '')
        self.assertEqual(self.recipe.other_tags, '')


class GetSessionKeyTests(TestCase):
    """
    Test get_session_key function.
    """

    def test_returns_create_key_when_no_id(self):
        """Returns create key when recipe_id is None."""
        result = get_session_key(recipe_id=None)
        self.assertEqual(result, 'recipe_form_data')

    def test_returns_update_key_with_id(self):
        """Returns update key with recipe_id."""
        result = get_session_key(recipe_id=123)
        self.assertEqual(result, 'recipe_update_123')