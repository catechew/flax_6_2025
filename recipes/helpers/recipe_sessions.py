from django.http import QueryDict
from recipes.helpers.recipe_form_helpers import load_temp_image


def rebuild_form_data(session_data, request, recipe):
    """ Rebuild form data and files from session. """
    form_data = QueryDict("", mutable=True)
    form_data.update(session_data["form_data"])

    files = load_temp_image(
        session_data.get("temp_image_path"),
        request.user.id,
        recipe.id if recipe else None,
    )
    return form_data, files

def save_form_to_session(session_data, post_data):
    """ Persist form fields to session. """
    session_data["form_data"] = dict(post_data.items())
    session_data["image_clear"] = post_data.get("image-clear", False)
