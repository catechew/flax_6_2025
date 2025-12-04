import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile


def _get_temp_file_prefix(user_id, recipe_id=None):
    """ Prefix for temp image filenames. """
    if recipe_id:
        return f"temp_update_{user_id}_{recipe_id}_"
    return f"temp_{user_id}_"

def save_temp_image(uploaded_file, user_id, recipe_id=None):
    """ Save uploaded image to a temp path. """
    if not uploaded_file:
        return None

    prefix = _get_temp_file_prefix(user_id, recipe_id)
    filename = f"{prefix}{uploaded_file.name}"
    return default_storage.save(
        f"temp/{filename}",
        ContentFile(uploaded_file.read()),
    )

def load_temp_image(temp_path, user_id, recipe_id=None):
    """ Load temp image and return as SimpleUploadedFile in dict. """
    if not temp_path or not default_storage.exists(temp_path):
        return {}

    with default_storage.open(temp_path, "rb") as f:
        prefix = _get_temp_file_prefix(user_id, recipe_id)
        filename = os.path.basename(temp_path).replace(prefix, "")
        return {"image": SimpleUploadedFile(filename, f.read())}

def cleanup_temp_image(temp_path):
    """ Delete temp image if it exists. """
    if temp_path and default_storage.exists(temp_path):
        default_storage.delete(temp_path)
