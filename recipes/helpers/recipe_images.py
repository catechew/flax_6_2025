from django.core.files.base import ContentFile


def copy_original_image(recipe, original_recipe):
    """ Copy image from original recipe when creating a modified version. """
    if not original_recipe or not original_recipe.image:
        return

    original_recipe.image.file.seek(0)
    recipe.image.save(
        original_recipe.image.name,
        ContentFile(original_recipe.image.file.read()),
        save=False,
    )
    original_recipe.image.file.seek(0)


def delete_image_if_requested(recipe, session_data, original_recipe, is_owner):
    """ Delete image when owner requests image removal. """
    if original_recipe and is_owner and session_data.get("image_clear"):
        if recipe.image:
            recipe.image.delete(save=False)
            recipe.image = None
