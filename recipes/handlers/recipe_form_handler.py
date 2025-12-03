from django.shortcuts import get_object_or_404, redirect
from recipes.models import Recipe
from recipes.forms.recipe_form import RecipeForm
from recipes.helpers.recipe_form_helpers import (
    get_session_key, 
    initialise_tag_session, 
    get_tag_action_from_request, 
    handle_tag_operation, 
    apply_tags_to_recipe,
    cleanup_session
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
    Handles recipe create/update workflow state and operations
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
        return (
            get_object_or_404(Recipe, id=self.recipe_id)
            if self.recipe_id else None
        )

    def _init_session(self):
        session = self.request.session
        if self.session_key not in session:
            session[self.session_key] = {}
            initialise_tag_session(session[self.session_key], self.recipe)
            if self.recipe:
                session[self.session_key]["is_owner"] = (
                    self.recipe.author == self.request.user
                )
        return session[self.session_key]

    @property
    def is_create_mode(self):
        return self.mode == "create"

    def handle_form_get(self):
        form = (
            RecipeForm(self.session_data["form_data"], instance=self.recipe)
            if "form_data" in self.session_data
            else RecipeForm(instance=self.recipe)
        )
        return render(
            self.request,
            "recipes/recipe_form.html",
            {"form": form, "mode": self.mode, "is_owner": self.is_owner},
        )

    def handle_form_post(self):
        form = RecipeForm(self.request.POST, self.request.FILES, instance=self.recipe)
        if not form.is_valid():
            return render(self.request, "recipes/recipe_form.html", {"form": form})

        save_form_to_session(self.session_data, self.request.POST)
        self.request.session.modified = True
        return redirect_to_tags(self)

    def finalise_recipe(self):
        form_data, files = rebuild_form_data(
            self.session_data, self.request, self.recipe
        )
        form = RecipeForm(form_data, files, instance=self.recipe)
        recipe = form.save(commit=False)

        prepare_recipe_author(
            recipe, self.request.user, self.recipe, self.is_owner
        )
        copy_original_image(recipe, self.recipe)
        delete_image_if_requested(
            recipe, self.session_data, self.recipe, self.is_owner
        )

        apply_tags_to_recipe(recipe, self.session_data)
        recipe.save()

        cleanup_session(self.session_key, self.session_data, self.request)
        show_success_message(self.request, self, recipe)

        return redirect("recipe_detail", recipe_id=recipe.id)