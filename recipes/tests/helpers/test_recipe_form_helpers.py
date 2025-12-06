from django.test import TestCase, RequestFactory
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.messages.storage.fallback import FallbackStorage
from recipes.handlers.recipe_form_handler import RecipeFormHandler
from recipes.helpers.recipe_form_helpers import get_tag_action_from_request
from recipes.models import Recipe, User
from django.utils import timezone
from unittest.mock import patch, MagicMock


class RecipeFormHelpersTestCase(TestCase):
    """
    Tests for RecipeFormHelper class.
    """
    fixtures = ['recipes/tests/fixtures/default_user.json', 'recipes/tests/fixtures/other_users.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.other_user = User.objects.get(username='@janedoe')
        self.recipe = Recipe.objects.create(
            title='Test Recipe', author=self.user, publication_date=timezone.now().date(),
            servings=4, ingredients='Test (1)', steps='Test steps', prep_time_hours=0,
            prep_time_minutes=30, cook_time_hours=1, cook_time_minutes=15, private=False)

    def get_request(self, user=None, method='GET'):
        """ Create a request with session and messages. """
        factory = RequestFactory()
        request = factory.get('/test/') if method == 'GET' else factory.post('/test/')
        request.user = user or self.user
        request.session = SessionStore()
        request.session.create()
        request._messages = FallbackStorage(request)
        return request

    def test_create_mode(self):
        """ Test handler in create mode. """
        request = self.get_request()
        handler = RecipeFormHandler(request, recipe_id=None)
        self.assertTrue(handler.is_create_mode)
        self.assertIsNone(handler.recipe)
        self.assertTrue(handler.is_owner)
        self.assertEqual(handler.mode, "create")

    def test_update_mode_owner(self):
        """ Test handler in update mode as owner. """
        request = self.get_request(user=self.user)
        handler = RecipeFormHandler(request, recipe_id=self.recipe.id)
        self.assertFalse(handler.is_create_mode)
        self.assertEqual(handler.recipe, self.recipe)
        self.assertTrue(handler.is_owner)
        self.assertEqual(handler.mode, "update")

    def test_update_mode_non_owner(self):
        """ Test handler in update mode as non-owner. """
        request = self.get_request(user=self.other_user)
        handler = RecipeFormHandler(request, recipe_id=self.recipe.id)
        self.assertFalse(handler.is_owner)

    def test_get_tags_context(self):
        """ Test tags context has required fields. """
        request = self.get_request()
        handler = RecipeFormHandler(request)
        context = handler.get_tags_context()
        for key in ['course_tags', 'dietary_tags', 'cuisine_tags', 'other_tags',
                    'has_image', 'mode', 'is_owner']:
            self.assertIn(key, context)

    def test_get_tags_context_with_recipe(self):
        """ Test tags context includes recipe in update mode. """
        request = self.get_request()
        handler = RecipeFormHandler(request, recipe_id=self.recipe.id)
        context = handler.get_tags_context()
        self.assertIn('recipe', context)
        self.assertIn('recipe_id', context)
        self.assertEqual(context['recipe'], self.recipe)

    def test_get_tags_context_without_recipe(self):
        """ Test tags context in create mode (no recipe). """
        request = self.get_request()
        handler = RecipeFormHandler(request)
        context = handler.get_tags_context()
        self.assertNotIn('recipe', context)
        self.assertNotIn('recipe_id', context)

    def test_redirect_to_cancel_destination_create_mode(self):
        """ Test cancel redirect in create mode. """
        request = self.get_request()
        handler = RecipeFormHandler(request)
        response = handler.redirect_to_cancel_destination()
        self.assertEqual(response.status_code, 302)
        self.assertIn('recipes', response.url)

    def test_redirect_to_cancel_destination_update_mode(self):
        """ Test cancel redirect in update mode. """
        request = self.get_request()
        handler = RecipeFormHandler(request, recipe_id=self.recipe.id)
        response = handler.redirect_to_cancel_destination()
        self.assertEqual(response.status_code, 302)
        self.assertIn('recipe', response.url)

    def test_handle_form_get_with_form_data(self):
        """ Test form is pre-populated from session. """
        request = self.get_request()
        handler = RecipeFormHandler(request)
        handler.session_data['form_data'] = {'title': 'Test'}
        response = handler.handle_form_get()
        self.assertEqual(response.status_code, 200)

    def test_handle_form_get_without_form_data(self):
        """ Test form is empty when no session data. """
        request = self.get_request()
        handler = RecipeFormHandler(request)
        response = handler.handle_form_get()
        self.assertEqual(response.status_code, 200)

    def test_session_key_create_mode(self):
        """ Test session key is correct for create mode. """
        request = self.get_request()
        handler = RecipeFormHandler(request)
        self.assertEqual(handler.session_key, 'recipe_form_data')

    def test_session_key_update_mode(self):
        """ Test session key is correct for update mode. """
        request = self.get_request()
        handler = RecipeFormHandler(request, recipe_id=self.recipe.id)
        self.assertEqual(handler.session_key, f'recipe_update_{self.recipe.id}')

    def test_show_missing_form_data_warning_message(self):
        """ Test warning message is shown. """
        request = self.get_request()
        handler = RecipeFormHandler(request)
        handler.show_missing_form_data_warning()
        messages = list(request._messages)
        self.assertTrue(any('fill in the recipe details' in str(m) for m in messages))

    def test_ai_dietary_tags_not_present(self):
        """ Test when AI dietary info is not in session. """
        request = self.get_request()
        handler = RecipeFormHandler(request)
        self.assertNotIn('ai_dietary_info', handler.session_data)
        self.assertIsNotNone(handler.session_data)

    def test_get_ai_prefill_data_returns_none_when_no_data(self):
        """ Test AI prefill returns None when no data in session. """
        request = self.get_request()
        request.session['from_ai_save_button'] = True
        handler = RecipeFormHandler(request)
        ai_data = handler._get_ai_prefill_data()
        self.assertIsNone(ai_data)

    def test_apply_ai_tags_if_available_empty(self):
        """ Test AI tags application with empty list. """
        request = self.get_request()
        handler = RecipeFormHandler(request)
        handler.session_data['ai_dietary_info'] = []
        handler._apply_ai_tags_if_available(handler.session_data)
        self.assertEqual(handler.session_data['ai_dietary_info'], [])

    @patch("recipes.handlers.recipe_form_handler.get_tag_action_from_request")
    @patch("recipes.handlers.recipe_form_handler.handle_tag_operation", return_value=True)
    @patch("recipes.handlers.recipe_form_handler.redirect_to_tags")
    def test_handle_tag_action_with_valid_action(self, mock_redirect, mock_handle, mock_get_action):
        """ Test handle_tag_action when action is valid. """
        mock_get_action.return_value = ('add', 'course', 'Breakfast')
        mock_redirect.return_value = MagicMock(status_code=302)
        request = self.get_request(method='POST')
        handler = RecipeFormHandler(request)
        response = handler.handle_tag_action()
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 302)
        mock_handle.assert_called_once_with(handler.session_data, 'add', 'course', 'Breakfast')
        mock_redirect.assert_called_once()

    @patch.object(RecipeFormHandler, "finalise_recipe")
    def test_handle_tags_post_calls_finalise(self, mock_final):
        """ Test handle_tags_post calls finalise_recipe. """
        request = self.get_request()
        request.POST = {"create_recipe": "1"}
        handler = RecipeFormHandler(request)
        handler.handle_tags_post()
        mock_final.assert_called_once()

    @patch.object(RecipeFormHandler, "handle_tag_action", return_value="OK")
    def test_handle_tags_post_calls_handle_tag_action(self, mock_action):
        """ Test handle_tags_post calls handle_tag_action. """
        request = self.get_request()
        request.POST = {}
        handler = RecipeFormHandler(request)
        result = handler.handle_tags_post()
        mock_action.assert_called_once()
        self.assertEqual(result, "OK")

    @patch("recipes.handlers.recipe_form_handler.rebuild_form_data", return_value=({}, {}))
    @patch("recipes.handlers.recipe_form_handler.cleanup_session")
    @patch("recipes.handlers.recipe_form_handler.show_success_message")
    def test_finalise_recipe_basic(self, mock_msg, mock_cleanup, mock_rebuild):
        """ Test finalise_recipe completes successfully. """
        request = self.get_request()
        handler = RecipeFormHandler(request, recipe_id=self.recipe.id)

        class FakeRecipe:
            id = 1

            def save(self): pass

        with patch("recipes.handlers.recipe_form_handler.RecipeForm") as MockForm:
            instance = MockForm.return_value
            instance.save.return_value = FakeRecipe()
            response = handler.finalise_recipe()
            self.assertEqual(response.status_code, 302)
            mock_cleanup.assert_called_once()

    def test_handle_tag_action_returns_none_when_no_action(self):
        """ Test tag action returns None when no action in POST. """
        request = self.get_request()
        handler = RecipeFormHandler(request)
        result = handler.handle_tag_action()
        self.assertIsNone(result)

    def test_cancel_recipe_operation_without_session(self):
        """ Test cancel operation when session key doesn't exist. """
        from recipes.views.recipe_cancel_view import cancel_recipe_operation
        request = self.get_request()
        request.session.flush()
        response = cancel_recipe_operation(request, recipe_id=None)
        self.assertEqual(response.status_code, 302)

    def test_update_mode_with_existing_session(self):
        """ Test handler uses existing session data. """
        request = self.get_request(user=self.user)
        request.session[f'recipe_update_{self.recipe.id}'] = {
            'is_owner': True, 'course_tags': ['breakfast']}
        handler = RecipeFormHandler(request, recipe_id=self.recipe.id)
        self.assertTrue(handler.is_owner)
        self.assertIn('course_tags', handler.session_data)

    def test_set_ownership_in_session_no_recipe(self):
        """ Test ownership not set when no recipe. """
        request = self.get_request()
        handler = RecipeFormHandler(request, recipe_id=None)
        session_copy = dict(handler.session_data)
        handler.set_ownership_in_session(handler.session_data)
        self.assertEqual(handler.session_data, session_copy)

    @patch("recipes.handlers.recipe_form_handler.apply_ai_dietary_tags")
    def test_apply_ai_tags_if_available_with_data(self, mock_apply):
        """ Test AI tags are applied when data exists. """
        request = self.get_request()
        handler = RecipeFormHandler(request)
        handler.session_data['ai_dietary_info'] = ['Vegan', 'Gluten-Free']
        handler._apply_ai_tags_if_available(handler.session_data)
        mock_apply.assert_called_once_with(handler.session_data, ['Vegan', 'Gluten-Free'])

    @patch("recipes.helpers.ai_recipe_parser.parse_ai_recipe_data")
    def test_get_ai_prefill_data_with_valid_data(self, mock_parse):
        """ Test AI prefill parsing when data exists. """
        mock_parse.return_value = {'title': 'AI Recipe'}
        request = self.get_request()
        request.session['from_ai_save_button'] = True
        request.session['ai_recipe_prefill'] = {'raw': 'data'}
        handler = RecipeFormHandler(request)
        result = handler._get_ai_prefill_data()
        self.assertIsNotNone(result)
        self.assertEqual(result, {'title': 'AI Recipe'})
        mock_parse.assert_called_once_with({'raw': 'data'})

    def test_handle_form_get_with_ai_prefill(self):
        """ Test form rendering with AI prefill data. """
        request = self.get_request()
        request.session['from_ai_save_button'] = True
        request.session['ai_recipe_prefill'] = {'title': 'AI Recipe', 'ingredients': ['flour', 'sugar']}
        with patch("recipes.helpers.ai_recipe_parser.parse_ai_recipe_data") as mock_parse:
            mock_parse.return_value = {'title': 'AI Recipe', 'ingredients': 'Flour (500g)\nSugar (200g)'}
            handler = RecipeFormHandler(request)
            response = handler.handle_form_get()
            self.assertEqual(response.status_code, 200)
            self.assertTrue(request.session.modified)

    def test_get_tags_context_with_temp_image(self):
        """ Test tags context shows has_image when temp image exists. """
        request = self.get_request()
        handler = RecipeFormHandler(request)
        handler.session_data['temp_image_path'] = '/tmp/test.jpg'
        context = handler.get_tags_context()
        self.assertTrue(context['has_image'])

    def test_get_tags_context_with_recipe_image(self):
        """ Test tags context shows has_image when recipe has image. """
        request = self.get_request()
        self.recipe.image = 'recipes/test.jpg'
        self.recipe.save()
        handler = RecipeFormHandler(request, recipe_id=self.recipe.id)
        context = handler.get_tags_context()
        self.assertTrue(context['has_image'])

    def test_handle_form_post_with_invalid_form(self):
        """ Test form POST with invalid data. """
        request = self.get_request(method='POST')
        request.POST = {'title': '', 'ingredients': 'Invalid'}
        handler = RecipeFormHandler(request)
        response = handler.handle_form_post()
        self.assertEqual(response.status_code, 200)

    @patch("recipes.handlers.recipe_form_handler.save_form_to_session")
    @patch("recipes.handlers.recipe_form_handler.redirect_to_tags")
    @patch("recipes.handlers.recipe_form_handler.RecipeForm")
    def test_handle_form_post_with_valid_form(self, MockForm, mock_redirect, mock_save):
        """ Test form POST with valid data. """
        mock_form_instance = MagicMock()
        mock_form_instance.is_valid.return_value = True
        MockForm.return_value = mock_form_instance
        mock_redirect.return_value = MagicMock(status_code=302)
        request = self.get_request(method='POST')
        request.POST = {'title': 'Test'}
        handler = RecipeFormHandler(request)
        response = handler.handle_form_post()
        self.assertEqual(response.status_code, 302)
        mock_save.assert_called_once()
        self.assertTrue(request.session.modified)

    @patch("recipes.handlers.recipe_form_handler.get_tag_action_from_request")
    @patch("recipes.handlers.recipe_form_handler.handle_tag_operation")
    def test_handle_tag_action_operation_fails(self, mock_handle, mock_get):
        """ Test tag action when operation returns False. """
        mock_get.return_value = ('add', 'course', 'Duplicate')
        mock_handle.return_value = False
        request = self.get_request(method='POST')
        handler = RecipeFormHandler(request)
        with patch("recipes.handlers.recipe_form_handler.redirect_to_tags") as mock_redirect:
            mock_redirect.return_value = MagicMock(status_code=302)
            response = handler.handle_tag_action()
            self.assertIsNotNone(response)
            mock_redirect.assert_called_once()

    def test_get_ai_prefill_when_ai_data_is_none(self):
        request = self.get_request()
        request.session['from_ai_save_button'] = True
        request.session['ai_recipe_prefill'] = None
        handler = RecipeFormHandler(request)
        result = handler._get_ai_prefill_data()
        self.assertIsNone(result)

    def test_get_tags_context_in_update_mode(self):
        request = self.get_request()
        handler = RecipeFormHandler(request, recipe_id=self.recipe.id)
        self.assertIsNotNone(handler.recipe)
        context = handler.get_tags_context()
        self.assertIn('recipe', context)
        self.assertEqual(context['recipe'], self.recipe)
        self.assertEqual(context['recipe_id'], self.recipe.id)

    def test_handle_tag_action_when_no_action_in_post(self):
        request = self.get_request(method='POST')
        request.POST = {}
        with patch("recipes.handlers.recipe_form_handler.get_tag_action_from_request") as mock_get:
            mock_get.return_value = (None, None, None)
            handler = RecipeFormHandler(request)
            result = handler.handle_tag_action()
            self.assertIsNone(result)

    def test_get_tag_action_from_request_no_valid_tag_actions(self):
        """
        test that function returns none tuple when post has no tag action keys
        """
        # Create a POST request with irrelevant data
        factory = RequestFactory()
        request = factory.post('/fake-url/', {
            'some_other_field': 'value',
            'another_field': 'another_value'
        })

        action, category, value = get_tag_action_from_request(request)

        self.assertIsNone(action)
        self.assertIsNone(category)
        self.assertIsNone(value)