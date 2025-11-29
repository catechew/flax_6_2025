from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch, MagicMock
from recipes.models import Recipe, User
from datetime import date


class AIRecipeFinderViewTestCase(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test',
            email='test@example.com',
            password='Pass123'
        )
        self.client.login(username='test', password='Pass123')
        self.url = reverse('ai_recipe_finder')
        
        self.recipe = Recipe.objects.create(
            title='Quick Pizza',
            author=self.user,
            publication_date=date.today(),
            ingredients='Dough\nCheese',
            steps='Bake',
            prep_time_minutes=15,
            cook_time_minutes=20
        )
    
    def test_get_shows_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Describe Your Situation')
    
    # sending a post with no context should show error
    def test_post_empty_context(self):
        response = self.client.post(self.url, {'context': ''})
        messages = list(response.context['messages'])
        self.assertIn('Please describe', str(messages[0]))
    
    # patch used to mock OpenAI API calls
    @patch('recipes.views.ai_recipe_finder_view.openai.ChatCompletion.create')
    def test_post_with_results(self, mock_openai):
        """POST with valid context returns results"""
        mock_search = MagicMock()
        mock_search.choices[0].message.content = '{"search_query": "pizza", "dietary_filters": [], "cuisine_filters": [], "other_filters": [], "sort_by": "date_newest"}'
        
        mock_ranking = MagicMock()
        mock_ranking.choices[0].message.content = '{"top_picks": [{"recipe_id": ' + str(self.recipe.id) + ', "title": "Quick Pizza", "reason": "Fast"}], "search_explanation": "Found pizza"}'
        
        mock_openai.side_effect = [mock_search, mock_ranking]
        
        response = self.client.post(self.url, {'context': 'I want pizza'})
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['show_results'])
        self.assertEqual(len(response.context['top_picks']), 1)
    
    @patch('recipes.views.ai_recipe_finder_view.openai.ChatCompletion.create')
    def test_post_no_results(self, mock_openai):
        """POST with no matching recipes"""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '{"search_query": "sushi", "dietary_filters": [], "cuisine_filters": ["Japanese"], "other_filters": [], "sort_by": "date_newest"}'
        mock_openai.return_value = mock_response
        
        response = self.client.post(self.url, {'context': 'I want sushi'})
        
        self.assertTrue(response.context['no_results'])
    
    @patch('recipes.views.ai_recipe_finder_view.openai.ChatCompletion.create')
    def test_api_error(self, mock_openai):
        """API errors handled gracefully"""
        mock_openai.side_effect = Exception('API Error')
        
        response = self.client.post(self.url, {'context': 'pizza'})
        messages = list(response.context['messages'])
        self.assertIn('An error occurred', str(messages[0]))
    
    def test_requires_login(self):
        """View requires authentication"""
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)