from django.shortcuts import get_object_or_404
from recipes.models import Recipe
from recipes.helpers.recipe_detail_helpers import (
    get_user_rating,
    has_user_flagged_recipe,
    get_recipe_tag_display_context,
    get_recipe_time_display_context,
    get_scaled_ingredients_context,
    get_cost_estimate_data,
)

class RecipeDetailHandler:
    """
    Handles recipe deail view workflow and context building
    """

    def __init__(self, request, recipe_id):
        self.request = request
        self.recipe_id = recipe_id
        self.recipe = self.get_recipe()
        self.desired_servings = self.parse_servings_param()
        self.is_owner = self.determine_ownership()

    def get_recipe(self):
        """Retrieve recipe or raise 404"""
        return get_object_or_404(Recipe, id=self.recipe_id)
    
    def parse_servings_param(self):
        """Parse servings from GET parameter, default to recipe servings"""
        servings_input = self.request.GET.get('servings', self.recipe.servings)
        try:
            servings = int(servings_input)
            return servings if servings > 0 else self.recipe.servings
        except (ValueError, TypeError):
            return self.recipe.servings
        
    def determine_ownership(self):
        """Check if current user owns the recipe"""
        if not self.request.user.is_authenticated:
            return False
        return self.recipe.author == self.request.user
    
    def get_user_context(self):
        """Build user-specific context (ratings, flags)"""
        return {
            'user_rating': get_user_rating(self.recipe, self.request.user),
            'user_has_flagged': has_user_flagged_recipe(self.recipe, self.request.user),
        }
    
    def get_cost_context(self):
        """return cost estimation context (cost estimate and cost error)"""
        cost_estimate = None
        cost_error = None

        if self.request.GET.get('show_cost') == 'true':
            try:
                cost_estimate = get_cost_estimate_data(scaled_ingredients, self.desired_servings)
            except Exception as e:
                cost_error = str(e)
        
        return{
            'cost_estimate' : cost_estimate,
            'cost_error' : cost_error
        }

    def get_context(self):
        """Create full context for recipe.html"""
        context = {
            'recipe': self.recipe,
            'steps': self.recipe.get_step_list(),
            'is_owner': self.is_owner,
        }

        # Add tag display
        context.update(get_recipe_tag_display_context(self.recipe))
        #Add time display
        context.update(get_recipe_time_display_context(self.recipe))
        #Add scaled ingredients
        scaling_context = get_scaled_ingredients_context(self.recipe, self.desired_servings)
        context.update(scaling_context)
        #Add cost estimation
        context.update(self.get_cost_context(scaling_context['scaled_ingredients']))
        #Add user data
        context.update(self.get_user_context())

        return context