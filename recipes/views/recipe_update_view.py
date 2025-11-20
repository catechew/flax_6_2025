from django.http import Http404, HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import render
from django.urls import reverse
from recipes.forms.recipe_form import RecipeForm
from recipes.models.recipe import Recipe


def recipe_update(request, recipe_id):
	try:
		recipe = Recipe.objects.get(id=recipe_id)
	except Recipe.DoesNotExist:
		raise Http404(f"Could not find recipe with primary key {recipe_id}") 
	
	is_owner = recipe.author == request.user
	
	if request.method == "POST" and not is_owner:
		messages.error(request, "You can only edit your own recipes.")
		return HttpResponseRedirect(request.path)          

	if request.method == "POST":
		form = RecipeForm(request.POST, request.FILES, instance=recipe)
		if form.is_valid():
			try:
				recipe = form.save()

				# Allow image deletion
				if request.POST.get('image-clear'):
					recipe.image.delete(save=False)
					recipe.image = None
				recipe.save()
			except:
				form.add_error(None, "It was not possible to save this recipe to the database.")
			else:
				messages.info(request, f"Updated recipe record to: {recipe}")
				path = reverse('all_recipes')
				return HttpResponseRedirect(path)
	else:
		form = RecipeForm(instance=recipe)
	return render(request, 'update_recipe.html', {'recipe_id': recipe_id, 'form': form})