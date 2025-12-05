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

from django.core.files.storage import default_storage

def save_form_to_session(session_data, post_data, files=None):
    """ Save recipe form data (and temp image) to session. """
    
    session_data["form_data"] = post_data.dict()

    # Save image-clear checkbox state
    if 'image-clear' in post_data:
        session_data['image_clear'] = True
    elif 'image_clear' in session_data:
        # Remove it if checkbox was previously checked but now unchecked
        del session_data['image_clear']

    if files and 'image' in files:
        image = files['image']
        temp_path = default_storage.save(f"temp/{image.name}", image)
        session_data['temp_image_path'] = temp_path

