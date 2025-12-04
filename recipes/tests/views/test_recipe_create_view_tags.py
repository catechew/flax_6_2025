from django.test import TestCase
from django.urls import reverse
from recipes.models import Recipe
from recipes.tests.utils import get_default_user, create_test_form_data


class RecipeCreateTagsTestCase(TestCase):
    """tests for recipe creation tags (page 2) functionality"""
    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json',
    ]

    def setUp(self):
        self.user = get_default_user()
        self.client.login(username='@johndoe', password='Password123')
        self.url = reverse('create_recipe')
        self.form_data = create_test_form_data()

    def test_create_recipe_tags_url(self):
        """test that page 2 url exists"""
        self.assertEqual(reverse('create_recipe_tags'), '/create_recipe/tags/')

    def test_get_create_recipe_tags_without_page1_redirects(self):
        """test accessing page 2 without completing page 1 redirects"""
        response = self.client.get(reverse('create_recipe_tags'))
        self.assertRedirects(response, reverse('create_recipe'))

    def test_get_create_recipe_tags_after_page1(self):
        """test accessing page 2 after completing page 1"""
        self.client.post(self.url, self.form_data, follow=True)
        response = self.client.get(reverse('create_recipe_tags'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/recipe_tags_form.html')

    def test_create_recipe_tags_context(self):
        """test that page 2 has required context variables"""
        self.client.post(self.url, self.form_data, follow=True)
        response = self.client.get(reverse('create_recipe_tags'))

        self.assertIn('course_tags', response.context)
        self.assertIn('dietary_tags', response.context)
        self.assertIn('cuisine_tags', response.context)
        self.assertIn('other_tags', response.context)
        self.assertIn('course_options', response.context)
        self.assertIn('dietary_options', response.context)
        self.assertIn('cuisine_options', response.context)
        self.assertIn('other_options', response.context)

    def test_add_course_tag(self):
        """test adding a course tag"""
        self.client.post(self.url, self.form_data, follow=True)
        self.client.post(reverse('create_recipe_tags'), {'add_course_tag': 'breakfast'})
        response = self.client.get(reverse('create_recipe_tags'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('breakfast', response.context['course_tags'])

    def test_add_dietary_tag(self):
        """test adding a dietary tag"""
        self.client.post(self.url, self.form_data, follow=True)
        response = self.client.post(reverse('create_recipe_tags'), {'add_dietary_tag': 'vegan'}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('vegan', response.context['dietary_tags'])

    def test_add_cuisine_tag(self):
        """test adding a cuisine tag"""
        self.client.post(self.url, self.form_data, follow=True)
        response = self.client.post(reverse('create_recipe_tags'), {'add_cuisine_tag': 'Italian'}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Italian', response.context['cuisine_tags'])

    def test_add_other_tag(self):
        """test adding an other tag"""
        self.client.post(self.url, self.form_data, follow=True)
        response = self.client.post(reverse('create_recipe_tags'), {'add_other_tag': 'quick'}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('quick', response.context['other_tags'])

    def test_add_duplicate_tag_ignored(self):
        """test that adding a duplicate tag is ignored"""
        self.client.post(self.url, self.form_data, follow=True)
        self.client.post(reverse('create_recipe_tags'), {'add_course_tag': 'breakfast'}, follow=True)
        self.client.post(reverse('create_recipe_tags'), {'add_course_tag': 'breakfast'})
        response = self.client.get(reverse('create_recipe_tags'))

        self.assertEqual(response.context['course_tags'].count('breakfast'), 1)

    def test_add_multiple_tags_same_category(self):
        """test adding multiple tags to same category"""
        self.client.post(self.url, self.form_data, follow=True)
        self.client.post(reverse('create_recipe_tags'), {'add_course_tag': 'breakfast'}, follow=True)
        response = self.client.post(reverse('create_recipe_tags'), {'add_course_tag': 'main'}, follow=True)

        self.assertIn('breakfast', response.context['course_tags'])
        self.assertIn('main', response.context['course_tags'])

    def test_add_custom_course_tag(self):
        """test adding a custom course tag"""
        self.client.post(self.url, self.form_data, follow=True)
        response = self.client.post(reverse('create_recipe_tags'), {
            'add_course_tag_custom': 'true',
            'course_tag_value': 'brunch'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('brunch', response.context['course_tags'])

    def test_add_custom_dietary_tag(self):
        """test adding a custom dietary tag"""
        self.client.post(self.url, self.form_data, follow=True)
        response = self.client.post(reverse('create_recipe_tags'), {
            'add_dietary_tag_custom': 'true',
            'dietary_tag_value': 'paleo'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('paleo', response.context['dietary_tags'])

    def test_add_custom_cuisine_tag(self):
        """test adding a custom cuisine tag"""
        self.client.post(self.url, self.form_data, follow=True)
        response = self.client.post(reverse('create_recipe_tags'), {
            'add_cuisine_tag_custom': 'true',
            'cuisine_tag_value': 'Mexican'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Mexican', response.context['cuisine_tags'])

    def test_add_custom_other_tag(self):
        """test adding a custom other tag"""
        self.client.post(self.url, self.form_data, follow=True)
        response = self.client.post(reverse('create_recipe_tags'), {
            'add_other_tag_custom': 'true',
            'other_tag_value': 'family-friendly'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('family-friendly', response.context['other_tags'])

    def test_remove_course_tag(self):
        """test removing a course tag"""
        self.client.post(self.url, self.form_data, follow=True)
        self.client.post(reverse('create_recipe_tags'), {'add_course_tag': 'breakfast'}, follow=True)
        response = self.client.post(reverse('create_recipe_tags'), {'remove_course_tag': 'breakfast'}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('breakfast', response.context['course_tags'])

    def test_remove_dietary_tag(self):
        """test removing a dietary tag"""
        self.client.post(self.url, self.form_data, follow=True)
        self.client.post(reverse('create_recipe_tags'), {'add_dietary_tag': 'vegan'}, follow=True)
        response = self.client.post(reverse('create_recipe_tags'), {'remove_dietary_tag': 'vegan'}, follow=True)

        self.assertNotIn('vegan', response.context['dietary_tags'])

    def test_remove_cuisine_tag(self):
        """test removing a cuisine tag"""
        self.client.post(self.url, self.form_data, follow=True)
        self.client.post(reverse('create_recipe_tags'), {'add_cuisine_tag': 'Italian'}, follow=True)
        response = self.client.post(reverse('create_recipe_tags'), {'remove_cuisine_tag': 'Italian'}, follow=True)

        self.assertNotIn('Italian', response.context['cuisine_tags'])

    def test_remove_other_tag(self):
        """test removing an other tag"""
        self.client.post(self.url, self.form_data, follow=True)
        self.client.post(reverse('create_recipe_tags'), {'add_other_tag': 'quick'}, follow=True)
        response = self.client.post(reverse('create_recipe_tags'), {'remove_other_tag': 'quick'}, follow=True)

        self.assertNotIn('quick', response.context['other_tags'])

    def test_remove_nonexistent_tag_ignored(self):
        """test that removing a tag that doesn't exist is handled gracefully"""
        self.client.post(self.url, self.form_data, follow=True)
        response = self.client.post(reverse('create_recipe_tags'), {'remove_course_tag': 'nonexistent'}, follow=True)

        self.assertEqual(response.status_code, 200)

    def test_add_empty_custom_tag_ignored(self):
        """test that adding empty custom tag is ignored"""
        self.client.post(self.url, self.form_data, follow=True)
        response = self.client.post(reverse('create_recipe_tags'), {
            'add_course_tag_custom': 'true',
            'course_tag_value': ''
        }, follow=True)

        self.assertEqual(len(response.context['course_tags']), 0)

    def test_create_recipe_with_tags(self):
        """test creating recipe with tags"""
        initial_count = Recipe.objects.count()
        self.client.post(self.url, self.form_data, follow=True)

        self.client.post(reverse('create_recipe_tags'), {'add_course_tag': 'main'}, follow=True)
        self.client.post(reverse('create_recipe_tags'), {'add_dietary_tag': 'vegan'}, follow=True)

        response = self.client.post(reverse('create_recipe_tags'), {'create_recipe': 'true'}, follow=True)

        self.assertEqual(Recipe.objects.count(), initial_count + 1)
        created_recipe = Recipe.objects.latest('id')
        self.assertIn('main', created_recipe.course_tags)
        self.assertIn('vegan', created_recipe.dietary_tags)

    def test_create_recipe_with_all_tag_types(self):
        """test creating recipe with all tag types"""
        initial_count = Recipe.objects.count()
        self.client.post(self.url, self.form_data, follow=True)

        self.client.post(reverse('create_recipe_tags'), {'add_course_tag': 'breakfast'}, follow=True)
        self.client.post(reverse('create_recipe_tags'), {'add_dietary_tag': 'vegetarian'}, follow=True)
        self.client.post(reverse('create_recipe_tags'), {'add_cuisine_tag': 'Italian'}, follow=True)
        self.client.post(reverse('create_recipe_tags'), {'add_other_tag': 'quick'}, follow=True)

        response = self.client.post(reverse('create_recipe_tags'), {'create_recipe': 'true'}, follow=True)

        self.assertEqual(Recipe.objects.count(), initial_count + 1)
        created_recipe = Recipe.objects.latest('id')
        self.assertEqual(created_recipe.course_tags, 'breakfast')
        self.assertEqual(created_recipe.dietary_tags, 'vegetarian')
        self.assertEqual(created_recipe.cuisine_tags, 'Italian')
        self.assertEqual(created_recipe.other_tags, 'quick')