import json
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from recipes.models import User, Recipe
from datetime import date
from django.contrib.messages import constants as message_constants
from recipes.tests.utils import AISearchTestMixin
from recipes.views.ai_recipe_search_view import (
    get_ai_rankings,
    apply_tag_filters,
    apply_search_query,
    apply_sorting,
)


class AIRecipeSearchViewTests(AISearchTestMixin, TestCase):
    """Test AI recipe search view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = self._create_user()
        self.recipe1 = self._create_recipe('Pasta Carbonara', 'vegetarian', 'Italian')
        self.recipe2 = self._create_recipe('Vegan Curry', 'vegan', 'Asian')
        self.url = reverse('ai_recipe_search')

    def _create_user(self):
        """Create test user."""
        return User.objects.create_user(
            username='@testuser', email='test@example.com',
            password='Password123', first_name='Test', last_name='User'
        )

    def _create_recipe(self, title, dietary, cuisine):
        """Create test recipe."""
        return Recipe.objects.create(
            author=self.user, title=title, publication_date=date.today(),
            ingredients=f'{title} (100g)', steps=f'Cook {title}',
            dietary_tags=dietary, cuisine_tags=cuisine
        )

    def test_redirect_if_not_logged_in(self):
        """Test redirect to login if not authenticated."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_get_displays_form(self):
        """Test GET displays search form."""
        self.client.login(username='@testuser', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ai/ai_recipe_search.html')

    def test_post_without_context_shows_error(self):
        """Test post without context shows error."""
        self.client.login(username='@testuser', password='Password123')
        response = self.client.post(self.url, {})
        messages = list(response.context['messages'])
        self.assertTrue(any('Please describe your situation' in str(m) for m in messages))

    def test_post_with_empty_context_shows_error(self):
        """Test post with empty context shows error."""
        self.client.login(username='@testuser', password='Password123')
        response = self.client.post(self.url, {'context': ''})
        messages = list(response.context['messages'])
        self.assertTrue(any('Please describe your situation' in str(m) for m in messages))

    @patch('openai.ChatCompletion.create')
    def test_successful_search_with_results(self, mock_openai):
        """Test successful search returns results."""
        self.client.login(username='@testuser', password='Password123')
        search_params = self.create_mock_search_params('vegan', dietary=['vegan'])
        ranking = self.create_mock_ranking(self.recipe2.id, 'Vegan Curry')
        mock_openai.side_effect = [search_params, ranking]
        response = self.client.post(self.url, {'context': 'I want vegan food'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['show_results'])
        self.assertIn('top_picks', response.context)

    @patch('openai.ChatCompletion.create')
    def test_search_with_no_results(self, mock_openai):
        """Test search with no matching recipes."""
        self.client.login(username='@testuser', password='Password123')
        search_params = self.create_mock_search_params('nonexistent')
        mock_openai.return_value = search_params
        response = self.client.post(self.url, {'context': 'I want something impossible'})
        self.assertTrue(response.context['no_results'])

    @patch('openai.ChatCompletion.create')
    def test_all_context_variables_present(self, mock_openai):
        """Test all required context variables are present."""
        self.client.login(username='@testuser', password='Password123')
        search_params = self.create_mock_search_params('pasta')
        ranking = self.create_mock_ranking(self.recipe1.id)
        mock_openai.side_effect = [search_params, ranking]
        response = self.client.post(self.url, {'context': 'I want pasta'})
        required = ['user_context', 'search_params', 'search_explanation',
                   'top_picks', 'top_pick_ids', 'total_count']
        for key in required:
            self.assertIn(key, response.context)

    @patch('openai.ChatCompletion.create')
    def test_user_context_preserved(self, mock_openai):
        """Test user input is preserved in context."""
        self.client.login(username='@testuser', password='Password123')
        search_params = self.create_mock_search_params('quick', other=['quick'])
        ranking = self.create_mock_ranking(self.recipe1.id)
        mock_openai.side_effect = [search_params, ranking]
        user_input = 'I need something quick for dinner'
        response = self.client.post(self.url, {'context': user_input})
        self.assertEqual(response.context['user_context'], user_input)

    @patch('openai.ChatCompletion.create')
    def test_openai_api_error(self, mock_openai):
        """Test openai api error shows error message."""
        self.client.login(username='@testuser', password='Password123')
        mock_openai.side_effect = Exception('API Error')
        response = self.client.post(self.url, {'context': 'I want pasta'})
        messages = list(response.context['messages'])
        self.assertTrue(any(m.level == message_constants.ERROR for m in messages))

    @patch('openai.ChatCompletion.create')
    def test_invalid_json_response(self, mock_openai):
        """Test invalid json from ai shows error."""
        self.client.login(username='@testuser', password='Password123')
        invalid = self.create_mock_search_params('')
        invalid.choices[0].message.content = 'not valid json'
        mock_openai.return_value = invalid
        response = self.client.post(self.url, {'context': 'I want pasta'})
        messages = list(response.context['messages'])
        self.assertTrue(any(m.level == message_constants.ERROR for m in messages))

    @patch('openai.ChatCompletion.create')
    def test_exception_preserves_user_context(self, mock_openai):
        """Test user context preserved on error."""
        self.client.login(username='@testuser', password='Password123')
        mock_openai.side_effect = Exception('Error')
        user_input = 'I want Italian food'
        response = self.client.post(self.url, {'context': user_input})
        self.assertEqual(response.context['user_context'], user_input)

    def test_apply_search_query_none(self):
        """Test apply_search_query with none."""
        recipes = Recipe.objects.all()
        result = apply_search_query(recipes, None)
        self.assertEqual(result.count(), 2)

    def test_apply_search_query_empty(self):
        """Test apply_search_query with empty string."""
        recipes = Recipe.objects.all()
        result = apply_search_query(recipes, '')
        self.assertEqual(result.count(), 2)

    def test_apply_tag_filters_empty(self):
        """Test apply_tag_filters with empty lists."""
        recipes = Recipe.objects.all()
        result = apply_tag_filters(recipes, [], [], [], [])
        self.assertEqual(result.count(), 2)

    def test_apply_tag_filters_single_course(self):
        """Test apply_tag_filters with course filter."""
        Recipe.objects.create(
            author=self.user, title='Breakfast', publication_date=date.today(),
            ingredients='Eggs', steps='Cook', course_tags='breakfast'
        )
        recipes = Recipe.objects.all()
        result = apply_tag_filters(recipes, ['breakfast'], [], [], [])
        self.assertEqual(result.count(), 1)

    def test_apply_tag_filters_with_other_tags(self):
        """Test apply_tag_filters with other tags."""
        Recipe.objects.create(
            author=self.user, title='Budget Meal', publication_date=date.today(),
            ingredients='Rice (200g)', steps='Cook rice', other_tags='budget'
        )
        recipes = Recipe.objects.all()
        result = apply_tag_filters(recipes, [], [], [], ['budget'])
        self.assertEqual(result.count(), 1)

    def test_apply_sorting_total_most(self):
        """Test sorting by total time most."""
        Recipe.objects.create(
            author=self.user, title='Long', publication_date=date.today(),
            ingredients='Long', steps='Long', prep_time_hours=5, prep_time_minutes=30,
            cook_time_hours=3, cook_time_minutes=15
        )
        recipes = Recipe.objects.all()
        result = apply_sorting(recipes, 'total_most')
        self.assertEqual(result.first().title, 'Long')

    def test_apply_sorting_invalid(self):
        """Test sorting with invalid option."""
        recipes = Recipe.objects.all()
        result = apply_sorting(recipes, 'invalid')
        self.assertIsNotNone(result)

    @patch('openai.ChatCompletion.create')
    def test_get_ai_rankings_empty_list(self, mock_openai):
        """Test rankings with empty recipe list."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "top_picks": [],
            "search_explanation": "No recipes"
        })
        mock_openai.return_value = mock_response

        result = get_ai_rankings('test', [])
        self.assertEqual(result['top_picks'], [])

    @patch('openai.ChatCompletion.create')
    def test_get_ai_rankings_single_recipe(self, mock_openai):
        """Test rankings with single recipe."""
        mock_openai.return_value = self.create_mock_ranking(self.recipe1.id)
        result = get_ai_rankings('test', [self.recipe1])
        self.assertEqual(len(result['top_picks']), 1)

    def test_whitespace_context(self):
        """Test whitespace only context."""
        self.client.login(username='@testuser', password='Password123')
        response = self.client.post(self.url, {'context': '   \n\t   '})
        messages = list(response.context['messages'])
        self.assertTrue(any(m.level == message_constants.ERROR for m in messages))

    def test_apply_tag_filters_multiple_dietary_and_cuisine(self):
        """Test multiple dietary filters."""
        recipes = Recipe.objects.all()
        result = apply_tag_filters(recipes, [], ['vegan', 'vegetarian'], ['Italian', 'Asian'], [])
        self.assertGreaterEqual(result.count(), 1)

    def test_apply_sorting_rating_high(self):
        """Test sorting by rating high."""
        recipes = Recipe.objects.all()
        result = apply_sorting(recipes, 'rating_high')
        self.assertIsNotNone(result)

    def test_apply_sorting_date_oldest(self):
        """Test sorting by date oldest."""
        recipes = Recipe.objects.all()
        result = apply_sorting(recipes, 'date_oldest')
        self.assertIsNotNone(result)

    def test_apply_search_query_matches_title(self):
        """Test search query matches title."""
        recipes = Recipe.objects.all()
        result = apply_search_query(recipes, 'Pasta')
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().title, 'Pasta Carbonara')

    def test_apply_search_query_matches_ingredients(self):
        """Test search query matches ingredients."""
        recipes = Recipe.objects.all()
        result = apply_search_query(recipes, 'Vegan Curry')
        self.assertEqual(result.count(), 1)

    def test_apply_tag_filters_single_dietary(self):
        """Test apply_tag_filters with single dietary filter."""
        recipes = Recipe.objects.all()
        result = apply_tag_filters(recipes, [], ['vegan'], [], [])
        self.assertEqual(result.count(), 1)

    def test_apply_tag_filters_single_cuisine(self):
        """Test apply_tag_filters with single cuisine filter."""
        recipes = Recipe.objects.all()
        result = apply_tag_filters(recipes, [], [], ['Italian'], [])
        self.assertEqual(result.count(), 1)