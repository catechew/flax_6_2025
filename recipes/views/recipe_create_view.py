from recipes.forms.recipe_form import RecipeForm
from django.views.generic.edit import CreateView
from django.urls import reverse
from recipes.models import Recipe



class CreateRecipeView(CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'create_recipe.html'

    def get_success_url(self):
        return reverse('all_recipes')