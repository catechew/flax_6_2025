from django.test import TestCase, RequestFactory
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.messages.storage.fallback import FallbackStorage
from recipes.handlers.recipe_form_handler import RecipeFormHandler
from recipes.models import Recipe, User, recipe
from django.utils import timezone
from unittest.mock import MagicMock



class RecipeFormHandlerTestCase(TestCase):

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json',
    ]

    def setUp(self):
        """Set up test fixtures"""
        self.user = User.objects.get(username='@johndoe')
        self.other_user = User.objects.get(username='@janedoe')
        
        # Create a test recipe
        self.recipe = Recipe.objects.create(
            title='Test Recipe',
            author=self.user,
            publication_date=timezone.now().date(),
            servings=4,
            ingredients='Test (1)',
            steps='Test steps',
            prep_time_hours=0,
            prep_time_minutes=30,
            cook_time_hours=1,
            cook_time_minutes=15,
            private=False
        )

    def get_request(self, user=None):
        """Create a GET request with session and messages"""
        factory = RequestFactory()
        request = factory.get('/test/')
        request.user = user or self.user
        
        # Add proper session
        request.session = SessionStore()
        request.session.create()
        
        # Add messages support
        setattr(request, '_messages', FallbackStorage(request))
        
        return request

    # Test create mode
    def test_create_mode(self):
        """Test handler in create mode"""
        request = self.get_request()
        handler = RecipeFormHandler(request, recipe_id=None)
        
        self.assertTrue(handler.is_create_mode)
        self.assertFalse(handler.is_update_mode)
        self.assertIsNone(handler.recipe)
        self.assertTrue(handler.is_owner)

    # Test update mode as owner
    def test_update_mode_owner(self):
        """Test handler in update mode as owner"""
        request = self.get_request(user=self.user)
        handler = RecipeFormHandler(request, recipe_id=self.recipe.id)
        
        self.assertFalse(handler.is_create_mode)
        self.assertTrue(handler.is_update_mode)
        self.assertEqual(handler.recipe, self.recipe)
        self.assertTrue(handler.is_owner)

    # Test update mode as non-owner
    def test_update_mode_non_owner(self):
        """Test handler in update mode as non-owner"""
        request = self.get_request(user=self.other_user)
        handler = RecipeFormHandler(request, recipe_id=self.recipe.id)
        
        self.assertFalse(handler.is_owner)

    # Test base context
    def test_get_base_context(self):
        """Test base context has required fields"""
        request = self.get_request()
        handler = RecipeFormHandler(request)
        context = handler.get_base_context()
        
        self.assertIn('mode', context)
        self.assertIn('is_owner', context)

    # Test tags context
    def test_get_tags_context(self):
        """Test tags context has tag fields"""
        request = self.get_request()
        handler = RecipeFormHandler(request)
        context = handler.get_tags_context()
        
        self.assertIn('course_tags', context)
        self.assertIn('dietary_tags', context)
        self.assertIn('has_image', context)

    # Test redirects work
    def test_redirect_methods(self):
        """Test all redirect methods return redirects"""
        request = self.get_request()
        handler = RecipeFormHandler(request)
        
        # Test each redirect returns a redirect response (status 302)
        self.assertEqual(handler.redirect_to_form_page().status_code, 302)
        self.assertEqual(handler.redirect_to_tags_page().status_code, 302)
        self.assertEqual(handler.redirect_to_detail_page(1).status_code, 302)
        self.assertEqual(handler.redirect_to_cancel_destination().status_code, 302)

    # Test session is marked modified
    def test_mark_session_modified(self):
        """Test session modified flag is set"""
        request = self.get_request()
        handler = RecipeFormHandler(request)
        
        handler.mark_session_modified()
        
        self.assertTrue(request.session.modified)

    def test_update_mode_with_existing_session(self):
        """Test handler uses existing session data in update mode"""
        request = self.get_request(user=self.user)
        # Pre-populate session
        request.session[f'recipe_update_{self.recipe.id}'] = {
            'is_owner': True,
            'original_author': '@johndoe'
        }
        
        handler = RecipeFormHandler(request, recipe_id=self.recipe.id)
        
        self.assertTrue(handler.is_owner)
        self.assertIn('original_author', handler.session_data)

    # Test base context in update mode
    def test_get_base_context_with_recipe(self):
        """Test base context includes recipe details in update mode"""
        request = self.get_request()
        handler = RecipeFormHandler(request, recipe_id=self.recipe.id)
        context = handler.get_base_context()
        
        self.assertIn('recipe', context)
        self.assertIn('recipe_id', context)
        self.assertIn('original_author', context)

    # Test redirect to form page in update mode
    def test_redirect_to_form_page_update_mode(self):
        """Test redirect to update form page"""
        request = self.get_request()
        handler = RecipeFormHandler(request, recipe_id=self.recipe.id)
        response = handler.redirect_to_form_page()
        
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(self.recipe.id), response.url)

    # Test redirect to tags page in update mode
    def test_redirect_to_tags_page_update_mode(self):
        """Test redirect to update tags page"""
        request = self.get_request()
        handler = RecipeFormHandler(request, recipe_id=self.recipe.id)
        response = handler.redirect_to_tags_page()
        
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(self.recipe.id), response.url)

    # Test cancel in update mode
    def test_redirect_to_cancel_destination_update_mode(self):
        """Test cancel redirect in update mode"""
        request = self.get_request()
        handler = RecipeFormHandler(request, recipe_id=self.recipe.id)
        response = handler.redirect_to_cancel_destination()
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('recipe', response.url)

    # Test show success message for non-owner with recipe
    def test_show_success_message_non_owner_with_recipe(self):
        """Test success message for non-owner includes original author note"""
        request = self.get_request(user=self.other_user)
        handler = RecipeFormHandler(request, recipe_id=self.recipe.id)
        handler.session_data['original_author'] = '@johndoe'
        
        handler.show_success_message(self.recipe)
        
        messages = list(request._messages)
        self.assertEqual(len(messages), 2)

    # Test handle_tag_action with no action
    def test_handle_tag_action_no_action(self):
        """Test handle_tag_action returns None when no action"""
        from unittest.mock import patch
        request = self.get_request()
        handler = RecipeFormHandler(request)
        
        with patch('recipes.handlers.recipe_form_handler.get_tag_action_from_request', return_value=(None, None, None)):
            result = handler.handle_tag_action()
        
        self.assertIsNone(result)

    # Test prepare_recipe_author for owner update
    def test_prepare_recipe_author_owner_update(self):
        """Test author not changed for owner update"""
        request = self.get_request()
        handler = RecipeFormHandler(request, recipe_id=self.recipe.id)
        
        handler.prepare_recipe_author(self.recipe, self.user, self.recipe, True)
        
        # Author should remain unchanged
        self.assertEqual(self.recipe.author, self.user)

    # Test handle_image_copy
    def test_handle_image_copy(self):
        """Test image is copied from original recipe"""
        request = self.get_request()
        handler = RecipeFormHandler(request)
        
        # Create mock recipes with images
        original = MagicMock()
        original.image.name = 'test.jpg'
        original.image.file.read.return_value = b'test_data'
        new_recipe = MagicMock()
        
        handler.handle_image_copy(new_recipe, original)
        
        # Verify image.save was called
        self.assertTrue(new_recipe.image.save.called)

    def test_handle_form_get_with_form_data(self):
        """Test form is pre-populated from session"""
        request = self.get_request()
        handler = RecipeFormHandler(request)
        handler.session_data['form_data'] = {'title': 'Test'}
        
        response = handler.handle_form_get()
        
        self.assertEqual(response.status_code, 200)

    def test_handle_form_get_without_form_data(self):
        """Test form is empty when no session data"""
        request = self.get_request()
        handler = RecipeFormHandler(request)
        
        response = handler.handle_form_get()
        
        self.assertEqual(response.status_code, 200)

    # Test form context with temp image
    def test_get_form_context_with_temp_image(self):
        """Test form context shows temp image when present"""
        from recipes.forms.recipe_form import RecipeForm
        request = self.get_request()
        handler = RecipeFormHandler(request)
        handler.session_data['temp_image_path'] = '/tmp/test.jpg'
        form = RecipeForm()
        
        context = handler.get_form_context(form)
        
        self.assertTrue(context['has_temp_image'])

    # Test tags context with temp image
    def test_get_tags_context_with_image(self):
        """Test tags context shows has_image when temp image exists"""
        request = self.get_request()
        handler = RecipeFormHandler(request)
        handler.session_data['temp_image_path'] = '/tmp/test.jpg'
        
        context = handler.get_tags_context()
        
        self.assertTrue(context['has_image'])

    # Test create form without instance
    def test_create_form_without_instance(self):
        """Test form creation without recipe instance"""
        request = self.get_request()
        handler = RecipeFormHandler(request)
        
        form = handler.create_form()
        
        self.assertIsNone(form.instance.pk)

    # Test create form with instance
    def test_create_form_with_instance(self):
        """Test form creation with recipe instance"""
        request = self.get_request()
        handler = RecipeFormHandler(request, recipe_id=self.recipe.id)
        
        form = handler.create_form()
        
        self.assertEqual(form.instance, self.recipe)