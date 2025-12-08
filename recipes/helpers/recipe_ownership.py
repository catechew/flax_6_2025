def determine_ownership(session_data):
    """ Return whether the current user owns the recipe. """
    return session_data.get("is_owner", True)

def prepare_recipe_author(recipe, user, original_recipe, is_owner):
    """ Assign correct author depending on create/update and ownership. """
    if original_recipe and not is_owner:
        recipe.pk = None
        recipe.id = None
        recipe.author = user
        return 

    if not original_recipe:
        recipe.author = user