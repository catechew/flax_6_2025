from django.shortcuts import get_object_or_404, redirect, render
from recipes.models import Recipe
from recipes.helpers.ai_recipe_parser import parse_ai_recipe_data
from recipes.forms.recipe_form import RecipeForm
from recipes.helpers.recipe_form_helpers import (
    get_session_key,
    initialise_tag_session,
    get_tag_context,
    get_tag_action_from_request,
    handle_tag_operation,
    apply_tags_to_recipe,
    get_ai_prefill_from_session,
    store_ai_dietary_info,
    apply_ai_dietary_tags,
    cleanup_session,
)
from recipes.helpers.recipe_ownership import (
    determine_ownership,
    prepare_recipe_author,
)
from recipes.helpers.recipe_images import (
    copy_original_image,
    delete_image_if_requested,
)
from recipes.helpers.recipe_sessions import (
    rebuild_form_data,
    save_form_to_session,
)
from recipes.helpers.recipe_redirects import (
    redirect_to_form,
    redirect_to_tags,
    show_success_message,
)


class RecipeFormHandler:
    """
    Handles recipe create/update workflow state and operations.
    """

    def __init__(self, request, recipe_id=None):
        self.request = request
        self.recipe_id = recipe_id
        self.mode = "create" if recipe_id is None else "update"
        self.recipe = self._get_recipe()
        self.session_key = get_session_key(recipe_id)
        self.session_data = self._init_session()
        self.is_owner = determine_ownership(self.session_data)

    def _get_recipe(self):
        """Get recipe or None."""
        return get_object_or_404(Recipe, id=self.recipe_id) if self.recipe_id else None

    def _init_session(self):
        """Initialise or get existing session."""
        session = self.request.session

        if self.session_key in session:
            return session[self.session_key]
        return self._create_new_session(session)

    def _create_new_session(self, session):
        """Create new session data."""
        session[self.session_key] = {}
        session_data = session[self.session_key]
        initialise_tag_session(session_data, self.recipe)
        self._apply_ai_tags_if_available(session_data)
        self.set_ownership_in_session(session_data)

        return session_data

    def _apply_ai_tags_if_available(self, session_data):
        """Apply AI dietary tags if present."""
        ai_dietary = session_data.get("ai_dietary_info", [])
        if ai_dietary:
            apply_ai_dietary_tags(session_data, ai_dietary)

    def set_ownership_in_session(self, session_data):
        """Set ownership flag in session if recipe exists."""
        if not self.recipe:
            return
        session_data["is_owner"] = self.recipe.author == self.request.user

    @property
    def is_create_mode(self):
        """Check if in create mode."""
        return self.mode == "create"

    def handle_form_get(self):
        """Handle GET request for form display."""
        ai_prefill = self._get_ai_prefill_data()

        if ai_prefill:
            return self._render_form_with_ai_data(ai_prefill)

        if "form_data" in self.session_data:
            return self._render_form_from_session()

        return self._render_empty_form()

    def _get_ai_prefill_data(self):
        """Get and parse AI prefill data."""
        if not self.request.session.pop("from_ai_save_button", False):
            return None

        ai_data = self.request.session.pop("ai_recipe_prefill", None)

        if not ai_data:
            return None

        from recipes.helpers.ai_recipe_parser import parse_ai_recipe_data

        return parse_ai_recipe_data(ai_data)

    def _render_form_with_ai_data(self, ai_prefill):
        """Render form with AI prefill data."""
        store_ai_dietary_info(self.session_data, ai_prefill)
        self.request.session.modified = True
        form = RecipeForm(initial=ai_prefill, instance=self.recipe)

        return self._render_form(form)

    def _render_form_from_session(self):
        """Render form from session data."""
        form = RecipeForm(self.session_data["form_data"], instance=self.recipe)
        return self._render_form(form)

    def _render_empty_form(self):
        """Render empty form."""
        form = RecipeForm(instance=self.recipe)
        return self._render_form(form)

    def _render_form(self, form):
        context = {
            "form": form,
            "mode": self.mode,
            "is_owner": self.is_owner,
            "recipe": self.recipe,
            "session_data": self.session_data,
            "original_author": (
                self.recipe.author.get_full_name()
                if self.recipe and self.recipe.author.get_full_name()
                else (self.recipe.author.username if self.recipe else None)
            ),
        }
        return render(self.request, "recipes/recipe_form.html", context)

    def handle_form_post(self):
        form = RecipeForm(self.request.POST, self.request.FILES, instance=self.recipe)

        if not form.is_valid():
            return render(self.request, "recipes/recipe_form.html", {"form": form})
        save_form_to_session(
            self.session_data,
            self.request.POST,
            self.request.FILES,
        )
        self.request.session.modified = True

        return redirect_to_tags(self)

    def finalise_recipe(self):
        """Finalise and save recipe."""
        recipe = self._prepare_recipe_for_save()
        self._apply_recipe_modifications(recipe)
        recipe.save()
        self._complete_recipe_workflow(recipe)

        return redirect("recipe_detail", recipe_id=recipe.id)

    def _prepare_recipe_for_save(self):
        """Build recipe instance from form data."""
        form_data, files = rebuild_form_data(
            self.session_data, self.request, self.recipe
        )
        form = RecipeForm(form_data, files, instance=self.recipe)
        recipe = form.save(commit=False)

        prepare_recipe_author(recipe, self.request.user, self.recipe, self.is_owner)
        return recipe

    def _apply_recipe_modifications(self, recipe):
        """Apply image and tag modifications to recipe."""
        copy_original_image(recipe, self.recipe)
        delete_image_if_requested(recipe, self.session_data, self.recipe, self.is_owner)
        apply_tags_to_recipe(recipe, self.session_data)

    def _complete_recipe_workflow(self, recipe):
        """Clean up session and show success message."""
        cleanup_session(self.session_key, self.session_data, self.request)
        show_success_message(self.request, self, recipe)

    def get_tags_context(self):
        """Build context for tags template."""
        context = self._build_base_context()

        if self.recipe:
            context.update(self._get_recipe_context())
        tag_data = get_tag_context(self.session_data)
        context.update(tag_data)
        context["has_image"] = self._check_has_image()

        return context

    def _build_base_context(self):
        """Build base context with mode and ownership."""
        return {
            "mode": self.mode,
            "is_owner": self.is_owner,
        }

    def _get_recipe_context(self):
        """Get recipe-specific context data."""
        return {
            "recipe": self.recipe,
            "recipe_id": self.recipe.id,
        }

    def _check_has_image(self):
        """Check if recipe has temp image or existing image."""
        return "temp_image_path" in self.session_data or (
            self.recipe and self.recipe.image
        )

    def handle_tag_action(self):
        """
        Handle add/remove tag actions from the tags page.
        Returns a redirect if an action was processed.
        """
        action, category, value = get_tag_action_from_request(self.request)

        if not action:
            return None

        if handle_tag_operation(self.session_data, action, category, value):
            self.request.session.modified = True

        return redirect_to_tags(self)

    def handle_tags_post(self):
        """Handle POST request for tag operations or recipe finalisation."""
        if "create_recipe" in self.request.POST or "update_recipe" in self.request.POST:
            return self.finalise_recipe()
        return self.handle_tag_action()

    def show_missing_form_data_warning(self):
        """Warn user and redirect if they try to access tag page."""
        from django.contrib import messages

        messages.warning(self.request, "Please fill in the recipe details first")
        return redirect_to_form(self)

    def redirect_to_cancel_destination(self):
        """
        Redirect after cancelling recipe create/update.
        Clears session data handled elsewhere.
        """
        if self.is_create_mode:
            return redirect("all_recipes")
        return redirect("recipe_detail", recipe_id=self.recipe_id)
