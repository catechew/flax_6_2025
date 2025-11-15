from django.http import Http404, HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import render
from django.urls import reverse
from recipes.forms.recipe_form import RecipeForm
from recipes.models.recipe import Recipe


def update_recipe(request, recipe_id):
	try:
		recipe = Recipe.objects.get(id=recipe_id)
	except Recipe.DoesNotExist:
		raise Http404(f"Could not find recipe with primary key {recipe_id}") 

	if request.method == "POST":
		form = RecipeForm(request.POST, instance=recipe)
		if form.is_valid():
			try:
				recipe = form.save()
			except:
				form.add_error(None, "It was not possible to save this recipe to the database.  Check the ISBN number.")
			else:
				messages.info(request, f"Updated recipe record to: {recipe}")
				path = reverse('list_recipes')
				return HttpResponseRedirect(path)
	else:
		form = RecipeForm(instance=recipe)
	return render(request, 'update_recipe.html', {'recipe_id': recipe_id, 'form': form})