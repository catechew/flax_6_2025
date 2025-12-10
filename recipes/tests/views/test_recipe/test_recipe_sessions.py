from django.test import TestCase
from django.http import QueryDict
from recipes.helpers.recipe_sessions import save_form_to_session


class RecipeSessionHelperTests(TestCase):
    """
    Tests for helper functions that store form data
    in the session during recipe creation/editing.
    """

    def test_save_form_sets_image_clear(self):
        """
        Ensure 'image_clear' is stored in the session
        when the POST data includes the image-clear flag.
        """
        session = {}
        post = QueryDict("", mutable=True)
        post["image-clear"] = "on"

        save_form_to_session(session, post)
        
        # image_clear should be True when flag is present
        self.assertTrue(session["image_clear"])

    def test_save_form_removes_image_clear(self):
        """
        Ensure 'image_clear' is removed from the session
        when the POST data does not contain the flag.
        """
        session = {"image_clear": True}
        post = QueryDict("", mutable=True)

        save_form_to_session(session, post)
        
        # image_clear sould no longer exist in the session
        self.assertNotIn("image_clear", session)