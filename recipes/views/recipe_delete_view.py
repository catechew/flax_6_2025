from django.http import Http404, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from recipes.models.recipe import Recipe
from recipes.models.user import User

def recipe_delete(request, recipe_id):
	try:
		recipe = Recipe.objects.get(id=recipe_id)
	except Recipe.DoesNotExist:
		raise Http404(f"Could not find recipe with primary key {recipe_id}") 
	
	# Only the recipe's author or an admin can delete it
	if recipe.author != request.user and not request.user.is_staff:
		return HttpResponseForbidden("You don't have permission to delete this recipe.\nYou must be an admin or author of this recipe.")

	if request.method == "POST":
		recipe.delete()
		path = reverse('all_recipes')
		return HttpResponseRedirect(path)
	else:
		return render(request, 'delete_recipe.html', {'recipe': recipe})