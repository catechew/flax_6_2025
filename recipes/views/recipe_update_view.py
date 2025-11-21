from django.http import Http404, HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from recipes.forms.recipe_form import RecipeForm
from recipes.models.recipe import Recipe
import os


def recipe_update(request, recipe_id):
	"""
	Page 1: Edit basic recipe information
	"""
	try:
		recipe = Recipe.objects.get(id=recipe_id)
	except Recipe.DoesNotExist:
		raise Http404(f"Could not find recipe with primary key {recipe_id}")

	is_owner = recipe.author == request.user

	if not is_owner:
		messages.error(request, "You can only edit your own recipes.")
		return redirect('recipe_detail', recipe_id=recipe_id)

	# Initialize session data for update if not exists
	session_key = f'recipe_update_{recipe_id}'
	if session_key not in request.session:
		request.session[session_key] = {
			'course_tags': recipe.get_course_tags_list(),
			'dietary_tags': recipe.get_dietary_tags_list(),
			'cuisine_tags' : recipe.get_cuisine_tags_list(),
			'other_tags': recipe.get_other_tags_list(),
		}

	session_data = request.session[session_key]

	if request.method == 'POST':
		form = RecipeForm(request.POST, request.FILES, instance=recipe)
		if form.is_valid():
			# Save form data to session (excluding file)
			form_dict = {}
			for key, value in request.POST.items():
				form_dict[key] = value

			session_data['form_data'] = form_dict
			session_data['image_clear'] = request.POST.get('image-clear', False)

			# Handle file upload - save temporarily to disk
			if request.FILES.get('image'):
				uploaded_file = request.FILES['image']
				# Save to temporary location
				temp_filename = f'temp_update_{request.user.id}_{recipe_id}_{uploaded_file.name}'
				temp_path = default_storage.save(f'temp/{temp_filename}', ContentFile(uploaded_file.read()))
				session_data['temp_image_path'] = temp_path

			request.session.modified = True

			# Redirect to page 2 (tag editing)
			return redirect('update_recipe_tags', recipe_id=recipe_id)
	else:
		# Pre-populate if coming back from page 2
		if 'form_data' in session_data:
			form = RecipeForm(session_data['form_data'], instance=recipe)
		else:
			form = RecipeForm(instance=recipe)

	context = {
		'recipe_id': recipe_id,
		'recipe': recipe,
		'form': form,
	}

	return render(request, 'update_recipe.html', context)


def update_recipe_tags(request, recipe_id):
	"""
	Page 2: Edit tags and save final changes
	"""
	try:
		recipe = Recipe.objects.get(id=recipe_id)
	except Recipe.DoesNotExist:
		raise Http404(f"Could not find recipe with primary key {recipe_id}")

	is_owner = recipe.author == request.user

	if not is_owner:
		messages.error(request, "You can only edit your own recipes.")
		return redirect('recipe_detail', recipe_id=recipe_id)

	session_key = f'recipe_update_{recipe_id}'

	# Redirect to page 1 if no form data in session
	if session_key not in request.session or 'form_data' not in request.session[session_key]:
		messages.warning(request, 'Please fill in the recipe details first.')
		return redirect('update_recipe', recipe_id=recipe_id)

	session_data = request.session[session_key]

	# Handle tag additions
	if request.method == 'POST' and 'add_course_tag' in request.POST:
		tag = request.POST.get('add_course_tag')
		if tag and tag not in session_data['course_tags']:
			session_data['course_tags'].append(tag)
			request.session.modified = True
		return redirect('update_recipe_tags', recipe_id=recipe_id)

	if request.method == 'POST' and 'add_dietary_tag' in request.POST:
		tag = request.POST.get('add_dietary_tag')
		if tag and tag not in session_data['dietary_tags']:
			session_data['dietary_tags'].append(tag)
			request.session.modified = True
		return redirect('update_recipe_tags', recipe_id=recipe_id)
	
	if request.method == 'POST' and 'add_cuisine_tag' in request.POST:
		tag = request.POST.get('add_cuisine_tag')
		if tag and tag not in session_data['cuisine_tags']:
			session_data['cuisine_tags'].append(tag)
			request.session.modified = True
		return redirect('update_recipe_tags', recipe_id=recipe_id)

	if request.method == 'POST' and 'add_other_tag' in request.POST:
		tag = request.POST.get('add_other_tag')
		if tag and tag not in session_data['other_tags']:
			session_data['other_tags'].append(tag)
			request.session.modified = True
		return redirect('update_recipe_tags', recipe_id=recipe_id)

	# Handle custom tag additions
	if request.method == 'POST' and 'add_course_tag_custom' in request.POST:
		tag = request.POST.get('course_tag_value')
		if tag and tag not in session_data['course_tags']:
			session_data['course_tags'].append(tag)
			request.session.modified = True
		return redirect('update_recipe_tags', recipe_id=recipe_id)

	if request.method == 'POST' and 'add_dietary_tag_custom' in request.POST:
		tag = request.POST.get('dietary_tag_value')
		if tag and tag not in session_data['dietary_tags']:
			session_data['dietary_tags'].append(tag)
			request.session.modified = True
		return redirect('update_recipe_tags', recipe_id=recipe_id)
	
	if request.method == 'POST' and 'add_cuisine_tag_custom' in request.POST:
		tag = request.POST.get('cuisine_tag_value')
		if tag and tag not in session_data['cuisine_tags']:
			session_data['cuisine_tags'].append(tag)
			request.session.modified = True
		return redirect('update_recipe_tags', recipe_id=recipe_id)

	if request.method == 'POST' and 'add_other_tag_custom' in request.POST:
		tag = request.POST.get('other_tag_value')
		if tag and tag not in session_data['other_tags']:
			session_data['other_tags'].append(tag)
			request.session.modified = True
		return redirect('update_recipe_tags', recipe_id=recipe_id)

	# Handle tag removals
	if request.method == 'POST' and 'remove_course_tag' in request.POST:
		tag = request.POST.get('remove_course_tag')
		if tag in session_data['course_tags']:
			session_data['course_tags'].remove(tag)
			request.session.modified = True
		return redirect('update_recipe_tags', recipe_id=recipe_id)

	if request.method == 'POST' and 'remove_dietary_tag' in request.POST:
		tag = request.POST.get('remove_dietary_tag')
		if tag in session_data['dietary_tags']:
			session_data['dietary_tags'].remove(tag)
			request.session.modified = True
		return redirect('update_recipe_tags', recipe_id=recipe_id)
	
	if request.method == 'POST' and 'remove_cuisine_tag' in request.POST:
		tag = request.POST.get('remove_cuisine_tag')
		if tag in session_data['cuisine_tags']:
			session_data['cuisine_tags'].remove(tag)
			request.session.modified = True
		return redirect('update_recipe_tags', recipe_id=recipe_id)

	if request.method == 'POST' and 'remove_other_tag' in request.POST:
		tag = request.POST.get('remove_other_tag')
		if tag in session_data['other_tags']:
			session_data['other_tags'].remove(tag)
			request.session.modified = True
		return redirect('update_recipe_tags', recipe_id=recipe_id)

	# Handle final recipe update
	if request.method == 'POST' and 'update_recipe' in request.POST:
		# Recreate form with saved data
		from django.http import QueryDict
		form_data = QueryDict('', mutable=True)
		form_data.update(session_data['form_data'])

		# Handle image if it exists
		files = {}
		if 'temp_image_path' in session_data:
			temp_path = session_data['temp_image_path']
			if default_storage.exists(temp_path):
				# Read the temp file
				with default_storage.open(temp_path, 'rb') as f:
					filename = os.path.basename(temp_path).replace(f'temp_update_{request.user.id}_{recipe_id}_', '')
					files = {'image': SimpleUploadedFile(filename, f.read())}

		form = RecipeForm(form_data, files, instance=recipe)

		if form.is_valid():
			try:
				recipe = form.save(commit=False)

				# Set tags from session
				recipe.course_tags = ','.join(session_data['course_tags'])
				recipe.dietary_tags = ','.join(session_data['dietary_tags'])
				recipe.cuisine_tags = ','.join(session_data['cuisine_tags'])
				recipe.other_tags = ','.join(session_data['other_tags'])

				# Handle image deletion
				if session_data.get('image_clear'):
					if recipe.image:
						recipe.image.delete(save=False)
					recipe.image = None

				recipe.save()

				# Delete temp image file if it exists
				if 'temp_image_path' in session_data:
					temp_path = session_data['temp_image_path']
					if default_storage.exists(temp_path):
						default_storage.delete(temp_path)

				# Clear session data
				del request.session[session_key]
				request.session.modified = True

				messages.success(request, f'Successfully updated recipe: {recipe.title}')
				return redirect('recipe_detail', recipe_id=recipe.id)
			except Exception as e:
				messages.error(request, f'Error updating recipe: {str(e)}')
				return redirect('update_recipe', recipe_id=recipe_id)
		else:
			# If validation fails, show errors
			messages.error(request, 'There was an error updating your recipe. Please check the form.')
			return redirect('update_recipe', recipe_id=recipe_id)

	# Predefined tag options
	course_options = ['dessert', 'main', 'appetiser', 'breakfast', 'snack']
	dietary_options = ['vegetarian', 'vegan', 'halal', 'kosher', 'gluten-free', 'dairy-free']
	cuisine_options = ['Japanese', 'Italian', 'Chinese', 'Asian', 'Persian', 'Jamaican', 'Western', 'British', 'Lebanese','Middle-Eastern']
	other_options = ['high protein', 'low calorie', 'low carb', 'quick', 'budget']

	context = {
		'recipe_id': recipe_id,
		'recipe': recipe,
		'course_tags': session_data['course_tags'],
		'dietary_tags': session_data['dietary_tags'],
		'cuisine_tags': session_data['cuisine_tags'],
		'other_tags': session_data['other_tags'],
		'course_options': course_options,
		'dietary_options': dietary_options,
		'cuisine_options': cuisine_options,
		'other_options': other_options,
	}

	return render(request, 'update_recipe_tags.html', context)


def cancel_recipe_update(request, recipe_id):
	"""Clear session data and redirect to recipe detail"""
	session_key = f'recipe_update_{recipe_id}'
	if session_key in request.session:
		# Clean up temp image file if it exists
		session_data = request.session[session_key]
		if 'temp_image_path' in session_data:
			temp_path = session_data['temp_image_path']
			if default_storage.exists(temp_path):
				default_storage.delete(temp_path)

		del request.session[session_key]

	request.session.modified = True
	messages.info(request, 'Recipe update cancelled.')
	return redirect('recipe_detail', recipe_id=recipe_id)