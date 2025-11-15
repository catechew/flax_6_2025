from recipes.forms.recipe_form import RecipeForm
from django.views.generic.edit import FormView
from django.urls import reverse


class CreateRecipeView(FormView):
    form_class = RecipeForm
    template_name = 'create_recipe.html'
    
    def form_valid(self, form):
        try:
            form.save()
        except:
            form.add_error(None, "It was not possible to save this recipe to the database.  Check the ISBN number.")
        else:
            return super().form_valid(form)

    def get_success_url(self):
        return reverse('list_recipes')