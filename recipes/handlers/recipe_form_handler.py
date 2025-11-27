from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from recipes.models import Recipe
from recipes.helpers.recipe_form_helpers import get_session_key, initialise_tag_session, get_tag_context
from recipes.forms.recipe_form import RecipeForm

class RecipeFormHandler:
    """Handles recipe create/update workflow state and operations"""

    def __init__(self, request, recipe_id=None):
        self.request = request
        self.recipe_id = recipe_id
        self.mode = 'create' if recipe_id is None else 'update'
        self.recipe = self._get_recipe()
        self.session_key = get_session_key(recipe_id)
        self.session_data = self._get_or_create_session_data()
        self.is_owner = self._determine_ownership()

    @property
    def is_create_mode(self):
        return self.mode == 'create'
    
    @property
    def is_update_mode(self):
        return self.mode == 'update'
    
    def _get_recipe(self):
        """Get recipe instance if update mode"""
        if self.recipe_id:
            return get_object_or_404(Recipe, id=self.recipe_id)
        return None
    
    def _get_or_create_session_data(self):
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
    
    def _determine_ownership(self):
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
        if self.recipe and self.is_owner:
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
                    f'Original recipe by {self.recipe.author.username} was not changed.'
                )

    def mark_session_modified(self):
        """Mark session as modified"""
        self.request.session.modified = True

