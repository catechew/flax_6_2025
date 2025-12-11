from django.http import QueryDict
from recipes.helpers.recipe_form_images import load_temp_image
from django.core.files.storage import default_storage

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

def save_form_to_session(session_data, post_data, files=None):
    """ Save recipe form data (and temp image) to session. """
    session_data["form_data"] = post_data.dict()
    _handle_image_clear_checkbox(session_data, post_data)
    _save_temp_image_if_present(session_data, files)

def _handle_image_clear_checkbox(session_data, post_data):
    """ Handle image-clear checkbox state. """
    if 'image-clear' in post_data:
        session_data['image_clear'] = True
        return 
    if 'image_clear' in session_data:
        del session_data['image_clear']

def _save_temp_image_if_present(session_data, files):
    """ Save uploaded image to temporary storage if present. """
    if not files or 'image' not in files:
        return
    image = files['image']
    temp_path = default_storage.save(f"temp/{image.name}", image)
    session_data['temp_image_path'] = temp_path