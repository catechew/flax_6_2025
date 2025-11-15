from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from recipes.models.recipe import Recipe

def delete_recipe(request, recipe_id):
	try:
		recipe = Recipe.objects.get(id=recipe_id)
	except Recipe.DoesNotExist:
		raise Http404(f"Could not find recipe with primary key {recipe_id}") 

	if request.method == "POST":
		recipe.delete()
		path = reverse('list_recipes')
		return HttpResponseRedirect(path)
	else:
		return render(request, 'delete_recipe.html', {'recipe': recipe})