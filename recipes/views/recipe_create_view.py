from recipes.forms.recipe_form import RecipeForm
from django.views.generic.edit import CreateView
from django.urls import reverse
from recipes.models import Recipe



class CreateRecipeView(CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'create_recipe.html'

    def form_valid(self, form):
        # Set author to current user
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('all_recipes')