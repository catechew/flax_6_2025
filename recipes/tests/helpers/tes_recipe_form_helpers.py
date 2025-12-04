from django.test import TestCase, RequestFactory
from recipes.helpers.recipe_form_helpers import(get_tag_action_from_request, handle_tag_operation, 
                                                initialise_tag_session)

class GetTagActionTests(TestCase):
    def test_add_custom_tag(self):
        factory = RequestFactory()
        request = factory.post("/", {
            "add_course_tag_custom": "on",
            "course_tag_value": "Dinner"
        })

        action, category, value = get_tag_action_from_request(request)

        self.assertEqual(action, "add")
        self.assertEqual(category, "course")
        self.assertEqual(value, "Dinner")

    def test_remove_tag(self):
        factory = RequestFactory()
        request = factory.post("/", {
            "remove_course_tag": "Dinner"
        })

        action, category, value = get_tag_action_from_request(request)

        self.assertEqual(action, "remove")
        self.assertEqual(category, "course")
        self.assertEqual(value, "Dinner")


class HandleTagOperationTests(TestCase):
    def test_remove_existing_tag(self):
        session_data = {"course_tags": ["Dinner"]}

        result = handle_tag_operation(
            session_data, "remove", "course", "Dinner"
        )

        self.assertTrue(result)
        self.assertEqual(session_data["course_tags"], [])
    
    def test_handle_tag_operation_invalid_input(self):
        result = handle_tag_operation({}, None, None, None)
        self.assertFalse(result)


class InitialiseTagSessionTests(TestCase):
    def test_initialise_empty_session(self):
        session = {}
        initialise_tag_session(session)

        self.assertEqual(session["course_tags"], [])
        self.assertEqual(session["dietary_tags"], [])
        self.assertEqual(session["cuisine_tags"], [])
        self.assertEqual(session["other_tags"], [])

