from django.test import TestCase
from django.urls import reverse
from recipes.models import Recipe, User
from django.utils import timezone 
from unittest.mock import patch

class RecipeDetailViewTestCase(TestCase):
    """Tests for the recipe detail view."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.client.login(username='@johndoe', password='Password123')

        self.recipe = Recipe.objects.create(
            author=self.user,
            title="Korean Noodles",                        
            publication_date=timezone.now().date(),
            ingredients="test (1)",
            steps="test"
        )
        self.url = reverse('recipe_detail', kwargs={'recipe_id': self.recipe.id})

    def test_recipe_detail_displays_course_tags(self):
        """Test that course tags are displayed"""
        recipe = Recipe.objects.create(
            author=self.user,
            title="Tagged Recipe",
            publication_date=timezone.now().date(),
            servings=4,
            ingredients="Eggs (2)",
            steps="Fry eggs",
            course_tags="breakfast,main"
        )

        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "breakfast")
        self.assertContains(response, "main")

    def test_recipe_detail_displays_dietary_tags(self):
        """Test that dietary tags are displayed"""
        recipe = Recipe.objects.create(
            author=self.user,
            title="Dietary Recipe",
            publication_date=timezone.now().date(),
            servings=4,
            ingredients="Tofu (200g)",
            steps="Cook tofu",
            dietary_tags="vegan,gluten-free"
        )

        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "vegan")
        self.assertContains(response, "gluten-free")

    def test_recipe_detail_displays_cuisine_tags(self):
        """Test that cuisine tags are displayed"""
        recipe = Recipe.objects.create(
            author=self.user,
            title="Cuisine Recipe",
            publication_date=timezone.now().date(),
            servings=4,
            ingredients="Pasta (300g)",
            steps="Cook pasta",
            cuisine_tags="Italian,Mediterranean"
        )

        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Italian")
        self.assertContains(response, "Mediterranean")

    def test_recipe_detail_displays_other_tags(self):
        """Test that other tags are displayed"""
        recipe = Recipe.objects.create(
            author=self.user,
            title="Quick Recipe",
            publication_date=timezone.now().date(),
            servings=2,
            ingredients="Bread (2 slices)",
            steps="Toast bread",
            other_tags="quick,budget"
        )

        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "quick")
        self.assertContains(response, "budget")

    def test_recipe_detail_with_all_tags(self):
        """Test recipe with all tag types displays correctly"""
        recipe = Recipe.objects.create(
            author=self.user,
            title="Fully Tagged Recipe",
            publication_date=timezone.now().date(),
            servings=4,
            ingredients="Rice (200g)",
            steps="Cook rice",
            course_tags="main",
            dietary_tags="vegan",
            cuisine_tags="Asian",
            other_tags="quick,budget"
        )

        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "main")
        self.assertContains(response, "vegan")
        self.assertContains(response, "Asian")
        self.assertContains(response, "quick")
        self.assertContains(response, "budget")

# Cost Estimation Tests

def test_cost_estimation_button_present(self):
    """Test that cost estimation button appears on page"""
    response = self.client.get(self.url)
    
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'Get Cost Estimate')
    self.assertContains(response, 'Cost Estimate')

def test_cost_estimation_not_calculated_by_default(self):
    """Test that cost is not calculated on initial page load"""
    response = self.client.get(self.url)
    
    self.assertEqual(response.status_code, 200)
    self.assertNotContains(response, 'Total Cost:')
    self.assertNotContains(response, 'Cost per Serving:')
    self.assertContains(response, 'Click the button to estimate')

@patch('recipes.views.recipe_detail_view.openai.ChatCompletion.create')
def test_cost_estimation_successful_response(self, mock_openai):
    """Test successful cost estimation returns and displays correctly"""
    # Mock OpenAI response
    mock_openai.return_value = type('obj', (object,), {
        'choices': [
            type('obj', (object,), {
                'message': type('obj', (object,), {
                    'content': '{"total_cost": 5.50, "cost_per_serving": 1.38, "currency": "GBP"}'
                })()
            })()
        ]
    })()
    
    recipe = Recipe.objects.create(
        author=self.user,
        title="Cost Test Recipe",
        publication_date=timezone.now().date(),
        servings=4,
        ingredients="Chicken (500g)\nRice (200g)",
        steps="Cook chicken and rice"
    )
    
    url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
    response = self.client.get(url, {'show_cost': 'true', 'servings': 4})
    
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'Total Cost:')
    self.assertContains(response, '£5.50')
    self.assertContains(response, 'Cost per Serving:')
    self.assertContains(response, '£1.38')
    self.assertContains(response, 'for 4 servings')

@patch('recipes.views.recipe_detail_view.openai.ChatCompletion.create')
def test_cost_estimation_with_scaled_servings(self, mock_openai):
    """Test cost estimation uses scaled servings correctly"""
    mock_openai.return_value = type('obj', (object,), {
        'choices': [
            type('obj', (object,), {
                'message': type('obj', (object,), {
                    'content': '{"total_cost": 11.00, "cost_per_serving": 1.38, "currency": "GBP"}'
                })()
            })()
        ]
    })()
    
    recipe = Recipe.objects.create(
        author=self.user,
        title="Scalable Cost Recipe",
        publication_date=timezone.now().date(),
        servings=4,
        ingredients="Pasta (400g)\nSauce (200ml)",
        steps="Cook pasta with sauce"
    )
    
    url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
    # Request with doubled servings
    response = self.client.get(url, {'show_cost': 'true', 'servings': 8})
    
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'for 8 servings')
    self.assertContains(response, '£11.00')

@patch('recipes.views.recipe_detail_view.openai.ChatCompletion.create')
def test_cost_estimation_openai_error_handling(self, mock_openai):
    """Test that OpenAI errors are handled gracefully"""
    # Mock OpenAI raising an error
    mock_openai.side_effect = Exception("API connection failed")
    
    recipe = Recipe.objects.create(
        author=self.user,
        title="Error Test Recipe",
        publication_date=timezone.now().date(),
        servings=2,
        ingredients="Bread (1 loaf)",
        steps="Toast bread"
    )
    
    url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
    response = self.client.get(url, {'show_cost': 'true'})
    
    self.assertEqual(response.status_code, 200)
    # Should display error message
    self.assertContains(response, 'Unexpected error')
    self.assertNotContains(response, 'Total Cost:')

@patch('recipes.views.recipe_detail_view.openai.ChatCompletion.create')
def test_cost_estimation_invalid_json_response(self, mock_openai):
    """Test handling of invalid JSON from AI"""
    # Mock OpenAI returning invalid JSON
    mock_openai.return_value = type('obj', (object,), {
        'choices': [
            type('obj', (object,), {
                'message': type('obj', (object,), {
                    'content': 'This is not valid JSON'
                })()
            })()
        ]
    })()
    
    recipe = Recipe.objects.create(
        author=self.user,
        title="Invalid JSON Test",
        publication_date=timezone.now().date(),
        servings=3,
        ingredients="Oil (2 tbsp)",
        steps="Heat oil"
    )
    
    url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
    response = self.client.get(url, {'show_cost': 'true'})
    
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'Failed to parse AI response')

@patch('recipes.views.recipe_detail_view.openai.ChatCompletion.create')
def test_cost_estimation_incomplete_json_response(self, mock_openai):
    """Test handling of incomplete data from AI"""
    # Mock OpenAI returning JSON missing required fields
    mock_openai.return_value = type('obj', (object,), {
        'choices': [
            type('obj', (object,), {
                'message': type('obj', (object,), {
                    'content': '{"total_cost": 5.00}'  # Missing cost_per_serving
                })()
            })()
        ]
    })()
    
    recipe = Recipe.objects.create(
        author=self.user,
        title="Incomplete Data Test",
        publication_date=timezone.now().date(),
        servings=2,
        ingredients="Eggs (4)",
        steps="Scramble eggs"
    )
    
    url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
    response = self.client.get(url, {'show_cost': 'true'})
    
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'Received incomplete data from AI')

def test_cost_estimation_persists_with_servings_change(self):
    """Test that cost parameter stays when recalculating servings"""
    response = self.client.get(self.url, {'show_cost': 'true', 'servings': 6})
    
    self.assertEqual(response.status_code, 200)
    # Form should preserve show_cost parameter
    self.assertContains(response, 'name="show_cost"')
    self.assertContains(response, 'value="true"')