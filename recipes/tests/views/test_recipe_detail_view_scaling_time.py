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

    def test_servings_scaling_doubles_ingredients(self):
          """Test that doubling servings doubles ingredient quantities"""
          recipe = Recipe.objects.create(
              author=self.user,
              title="Scalable Recipe",
              publication_date=timezone.now().date(),
              servings=2,
              ingredients="Sugar (100g)\nFlour (200g)",
              steps="Mix ingredients"
          )

          url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
          # Request with 4 servings (double the original 2)
          response = self.client.get(url, {'servings': 4})

          self.assertEqual(response.status_code, 200)
          # Check that quantities are doubled
          self.assertContains(response, "200")  # Sugar doubled from 100g
          self.assertContains(response, "400")  # Flour doubled from 200g

    def test_servings_scaling_halves_ingredients(self):
        """Test that halving servings halves ingredient quantities"""
        recipe = Recipe.objects.create(
            author=self.user,
            title="Halvable Recipe",
            publication_date=timezone.now().date(),
            servings=4,
            ingredients="Butter (200g)\nMilk (400ml)",
            steps="Mix ingredients"
        )

        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        # Request with 2 servings (half the original 4)
        response = self.client.get(url, {'servings': 2})

        self.assertEqual(response.status_code, 200)
        # Check that quantities are halved
        self.assertContains(response, "100")  # Butter halved from 200g
        self.assertContains(response, "200")  # Milk halved from 400ml

    def test_servings_with_invalid_value_uses_default(self):
        """Test that invalid servings value falls back to recipe default"""
        recipe = Recipe.objects.create(
            author=self.user,
            title="Default Servings Recipe",
            publication_date=timezone.now().date(),
            servings=3,
            ingredients="Rice (300g)",
            steps="Cook rice"
        )

        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        # Request with invalid servings
        response = self.client.get(url, {'servings': 'invalid'})

        self.assertEqual(response.status_code, 200)
        # Should use original 3 servings, so rice stays at 300g
        self.assertContains(response, "300")
        self.assertContains(response, "3")

    def test_servings_with_empty_value_uses_default(self):
        """Test that empty servings value falls back to recipe default"""
        recipe = Recipe.objects.create(
            author=self.user,
            title="Empty Servings Test",
            publication_date=timezone.now().date(),
            servings=5,
            ingredients="Pasta (500g)",
            steps="Boil pasta"
        )

        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        # Request with empty servings
        response = self.client.get(url, {'servings': ''})

        self.assertEqual(response.status_code, 200)
        # Should use original 5 servings
        self.assertContains(response, "500")
        self.assertContains(response, "5")

    def test_servings_scaling_factor_displayed(self):
        """Test that scaling factor is displayed when servings are adjusted"""
        recipe = Recipe.objects.create(
            author=self.user,
            title="Scaling Display Test",
            publication_date=timezone.now().date(),
            servings=2,
            ingredients="Salt (2g)",
            steps="Add salt"
        )

        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        # Request with 6 servings (3x the original)
        response = self.client.get(url, {'servings': 6})

        self.assertEqual(response.status_code, 200)
        # Check that scaling factor message appears
        self.assertContains(response, "scaled by")
        self.assertContains(response, "3.00")  # 6/2 = 3

    def test_recipe_detail_displays_prep_time(self):
        """Test that prep time is displayed when present"""
        recipe = Recipe.objects.create(
            author=self.user,
            title="Timed Recipe",
            publication_date=timezone.now().date(),
            servings=4,
            ingredients="Flour (500g)",
            steps="Mix flour",
            prep_time_hours=1,
            prep_time_minutes=30
        )

        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Prep:")
        self.assertContains(response, "1 hr 30 min")
    
    def test_recipe_detail_displays_prep_time_2(self):
        """Test that prep time is displayed when present"""
        # Prep time displayed as ... hrs if its more than 1 hr
        recipe = Recipe.objects.create(
            author=self.user,
            title="Timed Recipe",
            publication_date=timezone.now().date(),
            servings=4,
            ingredients="Flour (500g)",
            steps="Mix flour",
            prep_time_hours=2,
            prep_time_minutes=30
        )

        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Prep:")
        self.assertContains(response, "2 hrs 30 min")

    def test_recipe_detail_displays_cook_time(self):
        """Test that cook time is displayed when present"""
        recipe = Recipe.objects.create(
            author=self.user,
            title="Cooked Recipe",
            publication_date=timezone.now().date(),
            servings=4,
            ingredients="Chicken (1kg)",
            steps="Cook chicken",
            cook_time_hours=1,
            cook_time_minutes=15
        )

        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cook:")
        self.assertContains(response, "1 hr 15 min")

    def test_recipe_detail_displays_cook_time_2(self):
        """Test that cook time is displayed when present"""
        # Cook time displayed as ... hrs if its more than 1 hr
        recipe = Recipe.objects.create(
            author=self.user,
            title="Cooked Recipe",
            publication_date=timezone.now().date(),
            servings=4,
            ingredients="Chicken (1kg)",
            steps="Cook chicken",
            cook_time_hours=2,
            cook_time_minutes=15
        )

        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cook:")
        self.assertContains(response, "2 hrs 15 min")

    def test_recipe_detail_displays_total_time(self):
        """Test that total time is calculated and displayed"""
        recipe = Recipe.objects.create(
            author=self.user,
            title="Full Time Recipe",
            publication_date=timezone.now().date(),
            servings=4,
            ingredients="Pasta (500g)",
            steps="Cook pasta",
            prep_time_hours=0,
            prep_time_minutes=15,
            cook_time_hours=0,
            cook_time_minutes=25
        )

        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Total:")
        self.assertContains(response, "40 min")

    def test_recipe_detail_displays_total_time_2(self):
        """Test that total time is calculated and displayed"""
        # hrs for > 1 hr
        recipe = Recipe.objects.create(
            author=self.user,
            title="Full Time Recipe",
            publication_date=timezone.now().date(),
            servings=4,
            ingredients="Pasta (500g)",
            steps="Cook pasta",
            prep_time_hours=1,
            prep_time_minutes=15,
            cook_time_hours=1,
            cook_time_minutes=25
        )

        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Total:")
        self.assertContains(response, "2 hrs 40 min")
    
    def test_recipe_detail_displays_total_time_3(self):
        """Test that total time is calculated and displayed"""
        # hr for 1 hr
        recipe = Recipe.objects.create(
            author=self.user,
            title="Full Time Recipe",
            publication_date=timezone.now().date(),
            servings=4,
            ingredients="Pasta (500g)",
            steps="Cook pasta",
            prep_time_hours=0,
            prep_time_minutes=15,
            cook_time_hours=1,
            cook_time_minutes=25
        )

        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Total:")
        self.assertContains(response, "1 hr 40 min")


    def test_recipe_detail_with_zero_times_no_display(self):
        """Test that recipes with zero times don't show time sections"""
        recipe = Recipe.objects.create(
            author=self.user,
            title="No Time Recipe",
            publication_date=timezone.now().date(),
            servings=4,
            ingredients="Water (1L)",
            steps="Pour water",
            prep_time_hours=0,
            prep_time_minutes=0,
            cook_time_hours=0,
            cook_time_minutes=0
        )

        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        # Time sections should not appear
        self.assertNotContains(response, "Prep:")
        self.assertNotContains(response, "Cook:")

    def test_recipe_with_only_prep_time_minutes(self):
        """Test recipe with only minutes (no hours) displays correctly"""
        recipe = Recipe.objects.create(
            author=self.user,
            title="Quick Prep Recipe",
            publication_date=timezone.now().date(),
            servings=2,
            ingredients="Salad (1 bowl)",
            steps="Mix salad",
            prep_time_hours=0,
            prep_time_minutes=10
        )

        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "10 min")
        self.assertNotContains(response, "0 hr")

    def test_recipe_with_only_hours_no_minutes(self):
        """Test recipe with only hours (no minutes) displays correctly"""
        recipe = Recipe.objects.create(
            author=self.user,
            title="Long Cook Recipe",
            publication_date=timezone.now().date(),
            servings=6,
            ingredients="Stew (1 pot)",
            steps="Simmer stew",
            cook_time_hours=3,
            cook_time_minutes=0
        )

        url = reverse('recipe_detail', kwargs={'recipe_id': recipe.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "3 hrs")