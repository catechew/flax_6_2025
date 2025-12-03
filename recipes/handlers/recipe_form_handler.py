from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from recipes.models import Recipe
from django.shortcuts import render
from django.http import QueryDict
from django.core.files.base import ContentFile
from recipes.helpers.recipe_form_helpers import (
    get_session_key, 
    initialise_tag_session, 
    get_tag_context, 
    get_tag_action_from_request, 
    handle_tag_operation, 
    apply_tags_to_recipe,
    load_temp_image,
    save_temp_image,
    cleanup_session
)
from recipes.forms.recipe_form import RecipeForm


class RecipeFormHandler:
    """
    Handles recipe create/update workflow state and operations
    
    """

    def __init__(self, request, recipe_id=None):
        self.request = request
        self.recipe_id = recipe_id
        self.mode = 'create' if recipe_id is None else 'update'
        self.recipe = self.get_recipe()
        self.session_key = get_session_key(recipe_id)
        self.session_data = self.get_or_create_session_data()
        self.is_owner = self.determine_ownership()

    @property
    def is_create_mode(self):
        return self.mode == 'create'
    
    @property
    def is_update_mode(self):
        return self.mode == 'update'
    
    def get_recipe(self):
        """Get recipe instance if update mode"""
        if self.recipe_id:
            return get_object_or_404(Recipe, id=self.recipe_id)
        return None
    
    def get_or_create_session_data(self):
        """Get or initialise session data"""
        if self.session_key not in self.request.session:
            self.request.session[self.session_key] = {}
            initialise_tag_session(self.request.session[self.session_key], self.recipe)

            if self.recipe: #update mode
                self.request.session[self.session_key]['is_owner'] = (
                    self.recipe.author == self.request.user
                )
                self.request.session[self.session_key]['original_author'] = (
                    self.recipe.author.username
                )
        
        return self.request.session[self.session_key]
    
    def determine_ownership(self):
        """Determine if current user is the recipe owner"""
        return self.session_data.get('is_owner', True)
    
    def get_base_context(self):
        """Build base context shared by all templates"""
        context = {
            'mode' : self.mode,
            'is_owner' : self.is_owner
        }

        if self.recipe:
            context.update({
                'recipe' : self.recipe,
                'recipe_id': self.recipe.id,
                'original_author': self.recipe.author.username
            })
        return context
    
    def get_form_context(self, form):
        """Build context for recipe form template"""
        context = self.get_base_context()
        context['form'] = form
        context['has_temp_image'] = 'temp_image_path' in self.session_data
        return context
    
    def get_tags_context(self):
        """Build context for tags template"""
        context = self.get_base_context()
        tag_data = get_tag_context(self.session_data)
        context.update(tag_data)
        context['has_image'] = 'temp_image_path' in self.session_data
        return context
    
    def create_form(self, data=None, files=None):
        """Create RecipeForm with appropriate instance basedon mode and ownership"""
        if self.recipe:
            return RecipeForm(data, files, instance=self.recipe)
        return RecipeForm(data, files)

    def redirect_to_form_page(self):
        """Redirect to basic fields form page (step 1)"""
        if self.is_create_mode:
            return redirect('create_recipe')
        return redirect('update_recipe', recipe_id=self.recipe_id)
    
    def redirect_to_tags_page(self):
        """Redirect to tags page (step 2)"""
        if self.is_create_mode:
            return redirect('create_recipe_tags')
        return redirect('update_recipe_tags', recipe_id=self.recipe_id)
    
    def redirect_to_detail_page(self, recipe_id):
        """Redirect to recipe detail page"""
        return redirect('recipe_detail', recipe_id=recipe_id)
    
    def redirect_to_cancel_destination(self):
        """Redirect to appropriate page after cancellation"""
        if self.is_create_mode:
            messages.info(self.request, 'Recipe creation cancelled')
            return redirect('all_recipes')
        else:
            messages.info(self.request, 'Recipe update cancelled')
            return redirect('recipe_detail', recipe_id=self.recipe_id)
        
    def show_missing_form_data_warning(self):
        """Show warning and redirect when form data is missing"""
        messages.warning(self.request, 'Please fill in the recipe details first')
        return self.redirect_to_form_page()
    
    def show_success_message(self, saved_recipe):
        """Show appropriate success message based on mode and ownership"""
        if self.is_create_mode:
            messages.success(self.request, 'Recipe created successfully!')
        elif self.is_owner:
            messages.success(self.request, f'Successfully updated recipe: {saved_recipe.title}')
        else:
            messages.success(self.request, f'Created your modified version: {saved_recipe.title}')
            if self.recipe:
                messages.info(
                    self.request,
                    f'Original recipe by {self.session_data.get("original_author")} was not changed.'
                )

    def mark_session_modified(self):
        """Mark session as modified"""
        self.request.session.modified = True

    def handle_tag_action(self):
        """
        Handle tag add/remove actions
        Returns redirect if action was handled
        """
        action, category, value = get_tag_action_from_request(self.request)

        if not action:
            return None
        
        # Perform tag operation
        if handle_tag_operation(self.session_data, action, category, value):
            self.mark_session_modified()

        return self.redirect_to_tags_page()

    def prepare_recipe_author(self, recipe, user, original_recipe, is_owner):
        """Set appropriate author for recipe based on create/update mode"""
        if original_recipe and not is_owner:
            # non-owner creating a modified version/copy
            recipe.pk = None
            recipe.id = None
            recipe.author = user
        elif not original_recipe:
            # create mode
            recipe.author = user

    def handle_image_copy(self, recipe, original_recipe):
        """Copy image from original recipe for non-owner modification"""
        if original_recipe.image:
            original_recipe.image.file.seek(0)
            recipe.image.save(
                original_recipe.image.name,
                ContentFile(original_recipe.image.file.read()),
                save=False
            )
            original_recipe.image.file.seek(0) #reset for future use

    def handle_image_deletion(self, recipe, session_data, original_recipe, is_owner):
        """Delete recipe image"""
        if original_recipe and is_owner and session_data.get('image_clear'):
            if recipe.image:
                recipe.image.delete(save=False)
                recipe.image = None
        
    def prepare_form_data(self):
        """Recreate form data from session"""
        form_data = QueryDict('', mutable=True)
        form_data.update(self.session_data['form_data'])

        # Handle image file
        files = load_temp_image(
            self.session_data.get('temp_image_path'),
            self.request.user.id,
            self.recipe.id if self.recipe else None
        )
        return form_data, files
        
    def save_recipe_with_tags(self, form, session_data, user, original_recipe, is_owner):
        """Save recipe with tags and handle image operations"""
        recipe = form.save(commit=False)

        # Set author 
        self.prepare_recipe_author(recipe, user, original_recipe, is_owner)

        # Handle image operations
        if original_recipe and not is_owner:
            self.handle_image_copy(recipe, original_recipe)
        self.handle_image_deletion(recipe, session_data, original_recipe, is_owner)

        # Apply tags
        apply_tags_to_recipe(recipe, session_data)

        recipe.save()
        return recipe

    def finalise_recipe(self):
        """Create or update the recipe with form data and tags"""

        form_data, files = self.prepare_form_data()
        form = self.create_form(form_data, files)

        if not form.is_valid():
            context = self.get_form_context(form)
            return render(self.request, 'recipes/recipe_form.html', context)

        try:
            saved_recipe = self.save_recipe_with_tags(
                form, self.session_data, self.request.user, self.recipe, self.is_owner
            )

            cleanup_session(self.session_key, self.session_data, self.request)
            self.show_success_message(saved_recipe)
            return self.redirect_to_detail_page(saved_recipe.id)

        except Exception as e:
            messages.error(self.request, f'Error saving recipe: {str(e)}')
            return self.redirect_to_form_page()


    def handle_form_post(self):
        """Handle form submission"""

        image_uploaded = self.handle_image_in_session()

        post_data = self.request.POST.copy()
        files_data = self.request.FILES.copy() if not image_uploaded else {}

        form = self.create_form(post_data, files_data)

        if not form.is_valid():
            context = self.get_form_context(form)
            return render(self.request, 'recipes/recipe_form.html', context)

        self.save_form_to_session()
        self.mark_session_modified()

        return self.redirect_to_tags_page()


    def handle_form_get(self):
        """Handle form display"""
        # Pre-populate form if coming back from tags page
        if 'form_data' in self.session_data:
            form = self.create_form(self.session_data['form_data'])
        else:
            form = self.create_form()

        context = self.get_form_context(form)
        return render(self.request, 'recipes/recipe_form.html', context)

    def save_form_to_session(self):
        """Save form data to session""" 
        form_dict = {key: value for key, value in self.request.POST.items()}
        self.session_data['form_data'] = form_dict
        self.session_data['image_clear'] = self.request.POST.get('image-clear', False)

    def handle_image_in_session(self):
        """Handle image upload and save to temp location"""
        if self.request.FILES.get('image'):
            temp_path = save_temp_image(
                self.request.FILES['image'],
                self.request.user.id,
                self.recipe.id if self.recipe else None
            )
            if temp_path:
                self.session_data['temp_image_path'] = temp_path
                return True
        elif self.recipe and not self.recipe.author == self.request.user and self.recipe.image:
            # non-owner updating
            self.session_data['copy_original_image'] = True
        return False