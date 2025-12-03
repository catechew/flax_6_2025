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
    Handles recipe detail view workflow and context building.
    """

    def __init__(self, request, recipe_id):
        self.request = request
        self.recipe_id = recipe_id
        self.recipe = self.get_recipe()
        self.desired_servings = self.parse_servings_param()
        self.is_owner = self.determine_ownership()

    def _get_recipe(self, recipe_id):
        return get_object_or_404(Recipe, id=recipe_id)
    
    def _parse_servings_param(self):
        value = self.request.GET.get("servings", self.recipe.servings)
        try:
            servings = int(value)
            return servings if servings > 0 else self.recipe.servings
        except (TypeError, ValueError):
            return self.recipe.servings
        
    def _determine_ownership(self):
        user = self.request.user
        return user.is_authenticated and self.recipe.author == user
    
    def _user_context(self):
        """ Build user-specific context (ratings, flags). """
        
        return {
            "user_rating": get_user_rating(self.recipe, self.request.user),
            "user_has_flagged": has_user_flagged_recipe(
                self.recipe, self.request.user
            ),
        }
    
    def _cost_context(self, scaled_ingredients):
        if self.request.GET.get("show_cost") != "true":
            return {"cost_estimate": None, "cost_error": None}

        try:
            return {
                "cost_estimate": get_cost_estimate_data(
                    scaled_ingredients, self.desired_servings
                ),
                "cost_error": None,
            }
        except Exception as exc:
            return {"cost_estimate": None, "cost_error": str(exc)}

    def get_context(self):
        context = {
            'recipe': self.recipe,
            'steps': self.recipe.get_step_list(),
            'is_owner': self.is_owner,
        }

        context.update(get_recipe_tag_display_context(self.recipe))
        context.update(get_recipe_time_display_context(self.recipe))

        scaling = get_scaled_ingredients_context(
            self.recipe, self.desired_servings
        )
        context.update(scaling)
        context.update(self.get_cost_context(scaling["scaled_ingredients"]))
        context.update(self.get_user_context())

        return context