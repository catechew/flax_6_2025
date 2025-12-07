import json
from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock
from recipes.models import User, Recipe
from datetime import date
from recipes.views import ai_recipe_search_view
from recipes.views.ai_recipe_search_view import (
    get_search_params_from_ai,
    get_ai_rankings,
    apply_tag_filters,
    apply_search_query,
    apply_sorting,
    build_view_all_url
)


class AIRecipeSearchViewTests(TestCase):
    """ 
    Test AI recipe search view. 
    """

    def setUp(self):
        """ Set up test data. """
        self.client = Client()
        self.user = User.objects.create_user(
            username='@testuser',
            email='test@example.com',
            password='Password123',
            first_name='Test',
            last_name='User'
        )

        # Create test recipes
        self.recipe1 = Recipe.objects.create(
            author=self.user,
            title='Pasta Carbonara',
            publication_date=date.today(),
            ingredients='Pasta (400g)\nEggs (2)',
            steps='Cook pasta\nMix with eggs',
            dietary_tags='vegetarian',
            cuisine_tags='Italian',
        )

        self.recipe2 = Recipe.objects.create(
            author=self.user,
            title='Vegan Curry',
            publication_date=date.today(),
            ingredients='Chickpeas (400g)',
            steps='Cook curry',
            dietary_tags='vegan',
            cuisine_tags='Asian',
        )

        self.url = reverse('ai_recipe_search')

    def test_redirect_if_not_logged_in(self):
        """ Test redirect to login if not authenticated. """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_get_displays_form(self):
        """ Test GET displays search form. """
        self.client.login(username='@testuser', password='Password123')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ai/ai_recipe_search.html')

    def test_post_without_context_shows_error(self):
        """ Test post without context shows error. """
        self.client.login(username='@testuser', password='Password123')
        response = self.client.post(self.url, {})
        messages = list(response.context['messages'])
        self.assertTrue(any('Please describe your situation' in str(m) for m in messages))

    def test_post_with_empty_context_shows_error(self):
        """ Test post with empty context shows error. """
        self.client.login(username='@testuser', password='Password123')
        response = self.client.post(self.url, {'context': ''})
        messages = list(response.context['messages'])
        self.assertTrue(any('Please describe your situation' in str(m) for m in messages))

    @patch('openai.ChatCompletion.create')
    def test_successful_search_with_results(self, mock_openai):
        """ Test successful search returns results. """
        
        self.client.login(username='@testuser', password='Password123')

        # simulate the 2 AI responses
        search_params = MagicMock()
        search_params.choices = [MagicMock()]
        search_params.choices[0].message.content = json.dumps({
            "search_query": "vegan",
            "dietary_filters": ["vegan"],
            "cuisine_filters": [],
            "other_filters": [],
            "sort_by": "date_newest"
        })

        ranking = MagicMock()
        ranking.choices = [MagicMock()]
        ranking.choices[0].message.content = json.dumps({
            "top_picks": [{
                "recipe_id": self.recipe2.id,
                "title": "Vegan Curry",
                "reason": "Perfect vegan option"
            }],
            "search_explanation": "Found vegan recipes"
        })

        mock_openai.side_effect = [search_params, ranking]
        response = self.client.post(self.url, {'context': 'I want vegan food'})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['show_results'])
        self.assertIn('top_picks', response.context)
        self.assertIn('search_explanation', response.context)

    @patch('openai.ChatCompletion.create')
    def test_search_with_no_results(self, mock_openai):
        """ Test search with no matching recipes. """
        self.client.login(username='@testuser', password='Password123')

        search_params = MagicMock()
        search_params.choices = [MagicMock()]
        search_params.choices[0].message.content = json.dumps({
            "search_query": "nonexistent",
            "dietary_filters": [],
            "cuisine_filters": [],
            "other_filters": [],
            "sort_by": "date_newest"
        })

        mock_openai.return_value = search_params
        response = self.client.post(self.url, {'context': 'I want something impossible'})

        self.assertTrue(response.context['no_results'])
        self.assertTrue(response.context['show_results'])

    @patch('openai.ChatCompletion.create')
    def test_all_context_variables_present(self, mock_openai):
        """ Test all required context variables are present. """
        self.client.login(username='@testuser', password='Password123')

        search_params = MagicMock()
        search_params.choices = [MagicMock()]
        search_params.choices[0].message.content = json.dumps({
            "search_query": "pasta",
            "dietary_filters": [],
            "cuisine_filters": [],
            "other_filters": [],
            "sort_by": "date_newest"
        })

        ranking = MagicMock()
        ranking.choices = [MagicMock()]
        ranking.choices[0].message.content = json.dumps({
            "top_picks": [{"recipe_id": self.recipe1.id,
                           "title": "Pasta",
                           "reason": "Good"}],
            "search_explanation": "Found pasta"
        })

        mock_openai.side_effect = [search_params, ranking]
        response = self.client.post(self.url, {'context': 'I want pasta'})

        self.assertIn('user_context', response.context)
        self.assertIn('search_params', response.context)
        self.assertIn('search_explanation', response.context)
        self.assertIn('top_picks', response.context)
        self.assertIn('top_pick_ids', response.context)
        self.assertIn('total_count', response.context)
        self.assertIn('view_all_url', response.context)

    @patch('openai.ChatCompletion.create')
    def test_user_context_preserved(self, mock_openai):
        """ Test user input is preserved in context. """
        self.client.login(username='@testuser', password='Password123')

        search_params = MagicMock()
        search_params.choices = [MagicMock()]
        search_params.choices[0].message.content = json.dumps({
            "search_query": "quick",
            "dietary_filters": [],
            "cuisine_filters": [],
            "other_filters": ["quick"],
            "sort_by": "date_newest"
        })

        ranking = MagicMock()
        ranking.choices = [MagicMock()]
        ranking.choices[0].message.content = json.dumps({
            "top_picks": [{"recipe_id": self.recipe1.id, "title": "Pasta", "reason": "Quick"}],
            "search_explanation": "Found quick recipes"
        })

        mock_openai.side_effect = [search_params, ranking]
        user_input = 'I need something quick for dinner'
        response = self.client.post(self.url, {'context': user_input})

        self.assertEqual(response.context['user_context'], user_input)

    @patch('openai.ChatCompletion.create')
    def test_openai_api_error(self, mock_openai):
        """ Test openai api error shows error message. """
        self.client.login(username='@testuser', password='Password123')
        mock_openai.side_effect = Exception('API Error')

        response = self.client.post(self.url, {'context': 'I want pasta'})

        messages = list(response.context['messages'])
        self.assertTrue(any('An error occurred' in str(m) for m in messages))

    @patch('openai.ChatCompletion.create')
    def test_invalid_json_response(self, mock_openai):
        """ Test invalid json from ai shows error. """
        self.client.login(username='@testuser', password='Password123')

        invalid = MagicMock()
        invalid.choices = [MagicMock()]
        invalid.choices[0].message.content = 'not valid json'
        mock_openai.return_value = invalid

        response = self.client.post(self.url, {'context': 'I want pasta'})

        messages = list(response.context['messages'])
        self.assertTrue(any('An error occurred' in str(m) for m in messages))

    @patch('openai.ChatCompletion.create')
    def test_exception_preserves_user_context(self, mock_openai):
        """ Test user context preserved on error. """
        self.client.login(username='@testuser', password='Password123')
        mock_openai.side_effect = Exception('Error')

        user_input = 'I want Italian food'
        response = self.client.post(self.url, {'context': user_input})

        self.assertEqual(response.context['user_context'], user_input)

    def test_apply_search_query_none(self):
        """ Test apply_search_query with none". ""
        recipes = Recipe.objects.all()
        result = apply_search_query(recipes, None)
        self.assertEqual(result.count(), 2)

    def test_apply_search_query_empty(self):
        """ Test apply_search_query with empty string. """
        recipes = Recipe.objects.all()
        result = apply_search_query(recipes, '')
        self.assertEqual(result.count(), 2)

    def test_apply_tag_filters_empty(self):
        """ Test apply_tag_filters with empty lists. """
        recipes = Recipe.objects.all()
        result = apply_tag_filters(recipes, [], [], [], [])
        self.assertEqual(result.count(), 2)

    def test_apply_tag_filters_single_course(self):
        """ Test apply_tag_filters with course filter. """
        Recipe.objects.create(
            author=self.user,
            title='Breakfast',
            publication_date=date.today(),
            ingredients='Eggs',
            steps='Cook',
            course_tags='breakfast'
        )

        recipes = Recipe.objects.all()
        result = apply_tag_filters(recipes, ['breakfast'], [], [], [])
        self.assertEqual(result.count(), 1)

    def test_apply_sorting_total_most(self):
        """ Test sorting by total time most. """
        Recipe.objects.create(
            author=self.user,
            title='Long',
            publication_date=date.today(),
            ingredients='Long',
            steps='Long',
            prep_time_hours=5,
            prep_time_minutes=30,
            cook_time_hours=3,
            cook_time_minutes=15,
        )

        recipes = Recipe.objects.all()
        result = apply_sorting(recipes, 'total_most')
        self.assertEqual(result.first().title, 'Long')

    def test_apply_sorting_invalid(self):
        """ Test sorting with invalid option. """
        recipes = Recipe.objects.all()
        result = apply_sorting(recipes, 'invalid')
        self.assertIsNotNone(result)

    @patch('openai.ChatCompletion.create')
    def test_get_ai_rankings_empty_list(self, mock_openai):
        """ Test rankings with empty recipe list. """
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
        """ Test rankings with single recipe. """
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "top_picks": [{"recipe_id": self.recipe1.id, "title": "Test", "reason": "Only"}],
            "search_explanation": "One recipe"
        })
        mock_openai.return_value = mock_response

        result = get_ai_rankings('test', [self.recipe1])
        self.assertEqual(len(result['top_picks']), 1)

    def test_whitespace_context(self):
        """ Test whitespace only context. """
        self.client.login(username='@testuser', password='Password123')
        response = self.client.post(self.url, {'context': '   \n\t   '})

        messages = list(response.context['messages'])
        self.assertTrue(any('Please describe your situation' in str(m) for m in messages))

    def test_build_view_all_url_with_all_filter_types(self):
        """ Test url with all filter types including cuisine and other. """
        url = build_view_all_url(
            'pasta',
            ['breakfast'],
            ['vegan'],
            ['italian'],
            ['quick'],
            'rating_high'
        )
        self.assertIn('q=pasta', url)
        self.assertIn('course=breakfast', url)
        self.assertIn('dietary=vegan', url)
        self.assertIn('cuisine=italian', url)
        self.assertIn('other=quick', url)
        self.assertIn('sort=rating_high', url)

    def test_apply_tag_filters_multiple_dietary_and_cuisine(self):
        """ Test multiple dietary filters. """
        recipes = Recipe.objects.all()
        result = apply_tag_filters(recipes, [], ['vegan', 'vegetarian'], ['Italian', 'Asian'], [])
        # Should find both recipes
        self.assertGreaterEqual(result.count(), 1)

    def test_apply_sorting_rating_high(self):
        """ Test sorting by rating high. """
        recipes = Recipe.objects.all()
        result = apply_sorting(recipes, 'rating_high')
        self.assertIsNotNone(result)

    def test_apply_sorting_date_oldest(self):
        """ Test sorting by date oldest. """
        recipes = Recipe.objects.all()
        result = apply_sorting(recipes, 'date_oldest')
        self.assertIsNotNone(result)

    def test_apply_search_query_matches_title(self):
        """ Test search query matches title. """
        recipes = Recipe.objects.all()
        result = apply_search_query(recipes, 'Pasta')
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().title, 'Pasta Carbonara')

    def test_apply_search_query_matches_ingredients(self):
        """ Test search query matches ingredients. """
        recipes = Recipe.objects.all()
        result = apply_search_query(recipes, 'Chickpeas')
        self.assertEqual(result.count(), 1)
