from django.test import TestCase
from django.utils import timezone
from recipes.models import Recipe, User
from recipes.models.rating import Rating
from recipes.tests.utils import create_test_user, create_test_recipe

class RecipeModelTestCase(TestCase):
    """Tests for the Recipe model, including the __str__ method."""

    def setUp(self):
        self.user = create_test_user(username='@testuser')

        self.recipe = Recipe.objects.create(
            author=self.user,
            title="Korean Noodles",
            publication_date=timezone.now().date(),
            ingredients= "Garlic (5 cloves)\nSoy sauce (2 tbsp)",
            steps="Mix everything together\nFry the mixture",
        )

    def test_str_method(self):
        expected = (
            f"@testuser ({self.recipe.publication_date.year}) \"Korean Noodles\" "
            f"Adjectives: none.\n"
            f"Ingredients: Garlic (5 cloves)\nSoy sauce (2 tbsp)\n"
            f"Steps: Mix everything together\nFry the mixture"
        )
        self.assertEqual(str(self.recipe), expected)

    def test_get_ingredient_list(self):
      """Test that get_ingredient_list returns list of ingredients"""
      ingredients = self.recipe.get_ingredient_list()
      self.assertEqual(len(ingredients), 2)
      self.assertEqual(ingredients[0], "Garlic (5 cloves)")
      self.assertEqual(ingredients[1], "Soy sauce (2 tbsp)")

    def test_get_step_list(self):
        """Test that get_step_list returns list of steps"""
        steps = self.recipe.get_step_list()
        self.assertEqual(len(steps), 2)
        self.assertEqual(steps[0], "Mix everything together")
        self.assertEqual(steps[1], "Fry the mixture")

    def test_get_course_tags_list(self):
        """Test that get_course_tags_list returns list of course tags"""
        self.recipe.course_tags = "breakfast,main"
        self.recipe.save()
        tags = self.recipe.get_course_tags_list()
        self.assertEqual(len(tags), 2)
        self.assertIn("breakfast", tags)
        self.assertIn("main", tags)

    def test_get_dietary_tags_list(self):
        """Test that get_dietary_tags_list returns list of dietary tags"""
        self.recipe.dietary_tags = "vegan,gluten-free"
        self.recipe.save()
        tags = self.recipe.get_dietary_tags_list()
        self.assertEqual(len(tags), 2)
        self.assertIn("vegan", tags)
        self.assertIn("gluten-free", tags)

    def test_get_cuisine_tags_list(self):
        """Test that get_cuisine_tags_list returns list of cuisine tags"""
        self.recipe.cuisine_tags = "Italian,Japanese"
        self.recipe.save()
        tags = self.recipe.get_cuisine_tags_list()
        self.assertEqual(len(tags), 2)
        self.assertIn("Italian", tags)
        self.assertIn("Japanese", tags)

    def test_get_other_tags_list(self):
        """Test that get_other_tags_list returns list of other tags"""
        self.recipe.other_tags = "quick,budget"
        self.recipe.save()
        tags = self.recipe.get_other_tags_list()
        self.assertEqual(len(tags), 2)
        self.assertIn("quick", tags)
        self.assertIn("budget", tags)

    def test_get_all_tags_list(self):
        """Test that get_all_tags_list combines all tag types"""
        self.recipe.course_tags = "breakfast"
        self.recipe.dietary_tags = "vegan"
        self.recipe.cuisine_tags = "Italian"
        self.recipe.other_tags = "quick"
        self.recipe.save()

        all_tags = self.recipe.get_all_tags_list()
        self.assertEqual(len(all_tags), 4)
        self.assertIn("breakfast", all_tags)
        self.assertIn("vegan", all_tags)
        self.assertIn("Italian", all_tags)
        self.assertIn("quick", all_tags)

    def test_get_total_prep_time_minutes(self):
        """Test that total prep time is calculated correctly"""
        self.recipe.prep_time_hours = 1
        self.recipe.prep_time_minutes = 30
        self.recipe.save()

        total = self.recipe.get_total_prep_time_minutes()
        self.assertEqual(total, 90)  # 1 hour + 30 minutes = 90 minutes

    def test_get_total_cook_time_minutes(self):
        """Test that total cook time is calculated correctly"""
        self.recipe.cook_time_hours = 2
        self.recipe.cook_time_minutes = 15
        self.recipe.save()

        total = self.recipe.get_total_cook_time_minutes()
        self.assertEqual(total, 135)  # 2 hours + 15 minutes = 135 minutes

    def test_get_total_time_minutes(self):
        """Test that total time (prep + cook) is calculated correctly"""
        self.recipe.prep_time_hours = 1
        self.recipe.prep_time_minutes = 30
        self.recipe.cook_time_hours = 2
        self.recipe.cook_time_minutes = 15
        self.recipe.save()

        total = self.recipe.get_total_time_minutes()
        self.assertEqual(total, 225)  # 90 + 135 = 225 minutes

    def test_get_prep_time_display(self):
        """Test that prep time display formats correctly"""
        self.recipe.prep_time_hours = 1
        self.recipe.prep_time_minutes = 30
        self.recipe.save()

        display = self.recipe.get_prep_time_display()
        self.assertEqual(display, "1 hr 30 min")

    def test_get_prep_time_display_zero(self):
        """Test that zero prep time displays correctly"""
        self.recipe.prep_time_hours = 0
        self.recipe.prep_time_minutes = 0
        self.recipe.save()

        display = self.recipe.get_prep_time_display()
        self.assertEqual(display, "Not specified")

    def test_get_prep_time_display_only_hours(self):
        """Test prep time display with only hours"""
        self.recipe.prep_time_hours = 2
        self.recipe.prep_time_minutes = 0
        self.recipe.save()

        display = self.recipe.get_prep_time_display()
        self.assertEqual(display, "2 hrs")

    def test_get_prep_time_display_only_minutes(self):
        """Test prep time display with only minutes"""
        self.recipe.prep_time_hours = 0
        self.recipe.prep_time_minutes = 45
        self.recipe.save()

        display = self.recipe.get_prep_time_display()
        self.assertEqual(display, "45 min")

    def test_get_cook_time_display(self):
        """Test that cook time display formats correctly"""
        self.recipe.cook_time_hours = 2
        self.recipe.cook_time_minutes = 15
        self.recipe.save()

        display = self.recipe.get_cook_time_display()
        self.assertEqual(display, "2 hrs 15 min")

    def test_get_total_time_display(self):
        """Test that total time display formats correctly"""
        self.recipe.prep_time_hours = 0
        self.recipe.prep_time_minutes = 30
        self.recipe.cook_time_hours = 1
        self.recipe.cook_time_minutes = 10
        self.recipe.save()

        display = self.recipe.get_total_time_display()
        self.assertEqual(display, "1 hr 40 min")

    def test_adjectives_auto_populated_from_tags(self):
        """Test that adjectives field is auto-populated from tag fields on 
    save"""
        self.recipe.course_tags = "breakfast,main"
        self.recipe.dietary_tags = "vegan"
        self.recipe.cuisine_tags = "Italian"
        self.recipe.other_tags = "quick,budget"
        self.recipe.save()

        # adjectives should contain all tags
        self.assertIn("breakfast", self.recipe.adjectives)
        self.assertIn("main", self.recipe.adjectives)
        self.assertIn("vegan", self.recipe.adjectives)
        self.assertIn("Italian", self.recipe.adjectives)
        self.assertIn("quick", self.recipe.adjectives)
        self.assertIn("budget", self.recipe.adjectives)

    def test_empty_tags_result_in_none_adjectives(self):
        """Test that empty tags result in 'none' for adjectives"""
        self.recipe.course_tags = ""
        self.recipe.dietary_tags = ""
        self.recipe.cuisine_tags = ""
        self.recipe.other_tags = ""
        self.recipe.save()

        self.assertEqual(self.recipe.adjectives, "none")

    def test_tags_with_spaces_are_trimmed(self):
        """Test that tags with extra spaces are trimmed"""
        self.recipe.course_tags = " breakfast , main "
        self.recipe.save()

        tags = self.recipe.get_course_tags_list()
        self.assertEqual(tags[0], "breakfast")
        self.assertEqual(tags[1], "main")

    def test_empty_tag_list_returns_empty_list(self):
        """Test that empty tag fields return empty lists"""
        self.recipe.course_tags = ""
        self.recipe.save()

        tags = self.recipe.get_course_tags_list()
        self.assertEqual(len(tags), 0)
    
    def test_get_save_count(self):
        """Test that get_save_count returns correct number of saves"""

        # Create additional users
        user2 = User.objects.create_user(
            username='@testuser2',
            first_name='Test2',
            last_name='User2',
            email='test2@example.com',
            password='Password123'
        )
        user3 = User.objects.create_user(
            username='@testuser3',
            first_name='Test3',
            last_name='User3',
            email='test3@example.com',
            password='Password123'
        )

        # Initially should be 0
        self.assertEqual(self.recipe.get_save_count(), 0)

        # Add one save
        self.recipe.saved_by.add(self.user)
        self.assertEqual(self.recipe.get_save_count(), 1)

        # Add more saves
        self.recipe.saved_by.add(user2, user3)
        self.assertEqual(self.recipe.get_save_count(), 3)

        # Remove a save
        self.recipe.saved_by.remove(user2)
        self.assertEqual(self.recipe.get_save_count(), 2)

    def test_rating_count_initially_zero(self):
        """Test that a new recipe has 0 ratings."""
        self.assertEqual(self.recipe.rating_count(), 0)

    def test_average_rating_with_no_ratings(self):
        """Test that average rating is 0 when no ratings exist."""
        self.assertEqual(self.recipe.average_rating(), 0)

    def test_add_single_rating(self):
        """Test rating_count and average_rating with one rating."""
        Rating.objects.create(recipe=self.recipe, user=self.user, stars=4)
        self.assertEqual(self.recipe.rating_count(), 1)
        self.assertEqual(self.recipe.average_rating(), 4)
        self.assertEqual(self.recipe.average_rating_rounded(), 4)

    def test_multiple_ratings(self):
        """Test that average rating is computed correctly."""
        user2 = User.objects.create_user(
            username='@testuser2',
            first_name='Another',
            last_name='User',
            email='another@example.com',
            password='Password123'
        )

        Rating.objects.create(recipe=self.recipe, user=self.user, stars=5)
        Rating.objects.create(recipe=self.recipe, user=user2, stars=3)

        self.assertEqual(self.recipe.rating_count(), 2)
        self.assertAlmostEqual(self.recipe.average_rating(), 4.0)
        self.assertEqual(self.recipe.average_rating_rounded(), 4)

    def test_average_rating_rounding(self):
        """Test that rounding behaves as expected for display."""
        user2 = User.objects.create_user(
            username='@testuser2',
            first_name='Another',
            last_name='User',
            email='another@example.com',
            password='Password123'
        )

        Rating.objects.create(recipe=self.recipe, user=self.user, stars=5)
        Rating.objects.create(recipe=self.recipe, user=user2, stars=4)

        # Average = 4.5 rounded to 5
        self.assertAlmostEqual(self.recipe.average_rating(), 4.5)
        self.assertEqual(self.recipe.average_rating_rounded(), 5)