from django.test import TestCase, RequestFactory
from django.contrib.sessions.backends.db import SessionStore
from recipes.helpers.recipe_form_helpers import (
    cleanup_session,
    apply_ai_dietary_tags,
    get_ai_prefill_from_session,
    store_ai_dietary_info,
)
from unittest.mock import patch, MagicMock


class CleanupSessionTests(TestCase):
    """
    Test cleanup_session function.
    """

    @patch('recipes.helpers.recipe_form_helpers.cleanup_temp_image')
    def test_cleans_up_temp_image(self, mock_cleanup):
        session_data = {'temp_image_path': '/tmp/test.jpg'}
        request = MagicMock()
        request.session = SessionStore()
        request.session.create()
        request.session['recipe_form_data'] = session_data

        cleanup_session('recipe_form_data', session_data, request)
        mock_cleanup.assert_called_once_with('/tmp/test.jpg')

    @patch('recipes.helpers.recipe_form_helpers.cleanup_temp_image')
    def test_deletes_session_key(self, mock_cleanup):
        session_data = {}
        request = MagicMock()
        request.session = SessionStore()
        request.session.create()
        request.session['recipe_form_data'] = session_data

        cleanup_session('recipe_form_data', session_data, request)
        self.assertTrue(request.session.modified)
        self.assertNotIn('recipe_form_data', request.session)

    @patch('recipes.helpers.recipe_form_helpers.cleanup_temp_image')
    def test_handles_missing_session_key(self, mock_cleanup):
        session_data = {}
        request = MagicMock()
        request.session = SessionStore()
        request.session.create()

        cleanup_session('nonexistent_key', session_data, request)
        self.assertTrue(request.session.modified)


class ApplyAIDietaryTagsTests(TestCase):
    """
    Test apply_ai_dietary_tags function.
    """

    def test_does_nothing_when_no_ai_info(self):
        session_data = {'dietary_tags': ['existing']}
        apply_ai_dietary_tags(session_data, [])
        self.assertEqual(session_data['dietary_tags'], ['existing'])

    def test_does_nothing_when_none(self):
        session_data = {'dietary_tags': ['existing']}
        apply_ai_dietary_tags(session_data, None)
        self.assertEqual(session_data['dietary_tags'], ['existing'])

    @patch('recipes.helpers.ai_recipe_parser.map_ai_dietary_tags')
    def test_adds_mapped_tags(self, mock_map):
        mock_map.return_value = ['Vegan', 'Gluten-Free']
        session_data = {'dietary_tags': []}

        apply_ai_dietary_tags(session_data, ['vegan', 'gluten-free'])
        self.assertIn('Vegan', session_data['dietary_tags'])
        self.assertIn('Gluten-Free', session_data['dietary_tags'])

    @patch('recipes.helpers.ai_recipe_parser.map_ai_dietary_tags')
    def test_does_not_add_duplicates(self, mock_map):
        mock_map.return_value = ['Vegan']
        session_data = {'dietary_tags': ['Vegan']}

        apply_ai_dietary_tags(session_data, ['vegan'])
        self.assertEqual(session_data['dietary_tags'].count('Vegan'), 1)


class GetAIPrefillFromSessionTests(TestCase):
    """
    Test get_ai_prefill_from_session function.
    """

    def setUp(self):
        self.factory = RequestFactory()

    def test_returns_none_when_no_flag(self):
        request = self.factory.get('/test/')
        request.session = SessionStore()
        request.session.create()
        request.session['from_ai_save_button'] = False

        result = get_ai_prefill_from_session(request)
        self.assertIsNone(result)

    def test_returns_data_when_flag_true(self):
        request = self.factory.get('/test/')
        request.session = SessionStore()
        request.session.create()
        request.session['from_ai_save_button'] = True
        request.session['ai_recipe_prefill'] = {'title': 'Test'}

        result = get_ai_prefill_from_session(request)
        self.assertEqual(result, {'title': 'Test'})

    def test_pops_flag_from_session(self):
        request = self.factory.get('/test/')
        request.session = SessionStore()
        request.session.create()
        request.session['from_ai_save_button'] = True
        request.session['ai_recipe_prefill'] = {'title': 'Test'}

        get_ai_prefill_from_session(request)
        self.assertNotIn('from_ai_save_button', request.session)

    def test_pops_data_from_session(self):
        request = self.factory.get('/test/')
        request.session = SessionStore()
        request.session.create()
        request.session['from_ai_save_button'] = True
        request.session['ai_recipe_prefill'] = {'title': 'Test'}

        get_ai_prefill_from_session(request)
        self.assertNotIn('ai_recipe_prefill', request.session)


class StoreAIDietaryInfoTests(TestCase):
    """
    Test store_ai_dietary_info function.
    """

    def test_does_nothing_when_no_ai_info(self):
        session_data = {}
        ai_prefill = {'title': 'Test'}
        store_ai_dietary_info(session_data, ai_prefill)
        self.assertNotIn('ai_dietary_info', session_data)

    def test_stores_ai_dietary_info(self):
        session_data = {}
        ai_prefill = {'ai_dietary_info': ['vegan'], 'title': 'Test'}

        store_ai_dietary_info(session_data, ai_prefill)

        self.assertEqual(session_data['ai_dietary_info'], ['vegan'])
        self.assertNotIn('ai_dietary_info', ai_prefill)

    def test_stores_ai_description(self):
        session_data = {}
        ai_prefill = {
            'ai_dietary_info': ['vegan'],
            'ai_description': 'A delicious recipe'
        }

        store_ai_dietary_info(session_data, ai_prefill)
        self.assertEqual(session_data['ai_description'], 'A delicious recipe')
        self.assertNotIn('ai_description', ai_prefill)

    def test_handles_missing_description(self):
        session_data = {}
        ai_prefill = {'ai_dietary_info': ['vegan']}

        store_ai_dietary_info(session_data, ai_prefill)
        self.assertEqual(session_data['ai_description'], '')