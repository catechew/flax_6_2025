from django.test import TestCase, RequestFactory
from unittest.mock import MagicMock
from django.contrib.sessions.backends.db import SessionStore

from recipes.helpers.recipe_form_helpers import (
    get_tag_action_from_request,
    handle_tag_operation,
    initialise_tag_session,
    get_tag_list_for_key,
    cleanup_session,
    apply_ai_dietary_tags,
    get_ai_prefill_from_session,
    store_ai_dietary_info,
)


class GetTagActionTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_add_custom_tag(self):
        request = self.factory.post("/", {
            "add_course_tag_custom": "on",
            "course_tag_value": "Dinner"
        })
        action, category, value = get_tag_action_from_request(request)
        self.assertEqual(action, "add")
        self.assertEqual(category, "course")
        self.assertEqual(value, "Dinner")

    def test_remove_tag(self):
        request = self.factory.post("/", {
            "remove_course_tag": "Dinner"
        })
        action, category, value = get_tag_action_from_request(request)
        self.assertEqual(action, "remove")
        self.assertEqual(category, "course")
        self.assertEqual(value, "Dinner")


class GetTagActionMissingBranchesTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_non_post_request_returns_none(self):
        request = self.factory.get("/")
        self.assertEqual(
            get_tag_action_from_request(request),
            (None, None, None)
        )

    def test_no_valid_results_returns_none(self):
        request = self.factory.post("/", {})  # no tag info
        self.assertEqual(
            get_tag_action_from_request(request),
            (None, None, None)
        )


class CheckCategoryNoMatchTests(TestCase):
    def test_no_keys_match_returns_default(self):
        request = RequestFactory().post("/", {})
        from recipes.helpers.recipe_form_helpers import check_category_for_tag_action

        result = check_category_for_tag_action(request, "course")
        self.assertEqual(result, (None, None, None))


class HandleTagOperationTests(TestCase):
    def test_remove_existing_tag(self):
        session_data = {"course_tags": ["Dinner"]}
        result = handle_tag_operation(session_data, "remove", "course", "Dinner")

        self.assertTrue(result)
        self.assertEqual(session_data["course_tags"], [])

    def test_handle_tag_operation_invalid_inputs(self):
        self.assertFalse(handle_tag_operation({}, None, None, None))

    def test_add_new_tag(self):
        session = {"course_tags": []}
        result = handle_tag_operation(session, "add", "course", "Dinner")

        self.assertTrue(result)
        self.assertEqual(session["course_tags"], ["Dinner"])

    def test_add_existing_tag_no_duplicate(self):
        session = {"course_tags": ["Dinner"]}
        result = handle_tag_operation(session, "add", "course", "Dinner")

        self.assertTrue(result)
        self.assertEqual(session["course_tags"], ["Dinner"])


class HandleTagOperationEdgeCasesTests(TestCase):
    def test_reject_blank_value(self):
        session = {"course_tags": []}
        result = handle_tag_operation(session, "add", "course", "   ")
        self.assertFalse(result)

    def test_reject_value_too_long(self):
        session = {"course_tags": []}
        long_val = "x" * 51
        result = handle_tag_operation(session, "add", "course", long_val)
        self.assertFalse(result)


class InitialiseTagSessionTests(TestCase):
    def test_initialise_empty_session(self):
        session = {}
        initialise_tag_session(session)

        self.assertEqual(session["course_tags"], [])
        self.assertEqual(session["dietary_tags"], [])
        self.assertEqual(session["cuisine_tags"], [])
        self.assertEqual(session["other_tags"], [])


class GetTagListForKeyTests(TestCase):
    def test_returns_empty_list_if_recipe_none(self):
        result = get_tag_list_for_key(None, "course")
        self.assertEqual(result, [])


class CleanupSessionTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_cleanup_when_key_not_present(self):
        request = self.factory.get("/")
        request.session = SessionStore()

        cleanup_session("nonexistent_key", request.session, request)

        self.assertTrue(request.session.modified)

    def test_cleanup_when_key_present(self):
        request = self.factory.get("/")
        
        session = SessionStore()           
        session["recipe_form_data"] = {}
        session["temp_image_path"] = None

        request.session = session         

        cleanup_session("recipe_form_data", request.session, request)

        self.assertNotIn("recipe_form_data", request.session)
        self.assertTrue(request.session.modified)


class ApplyAIDietaryTagsTests(TestCase):
    def test_no_ai_info_does_nothing(self):
        session = {"dietary_tags": []}
        apply_ai_dietary_tags(session, None)
        self.assertEqual(session["dietary_tags"], [])

    def test_adds_new_ai_tags(self):
        session = {"dietary_tags": []}
        apply_ai_dietary_tags(session, ["Vegan"])
        self.assertEqual(session["dietary_tags"], ["Vegan"])

    def test_does_not_duplicate_tags(self):
        session = {"dietary_tags": ["Vegan"]}
        apply_ai_dietary_tags(session, ["Vegan"])
        self.assertEqual(session["dietary_tags"], ["Vegan"])


class GetAIPrefillTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_returns_none_when_flag_false(self):
        request = self.factory.get("/")
        request.session = SessionStore()

        result = get_ai_prefill_from_session(request)
        self.assertIsNone(result)

    def test_returns_and_removes_prefill_when_flag_true(self):
        request = self.factory.get("/")
        request.session = {
            "from_ai_save_button": True,
            "ai_recipe_prefill": {"title": "Pizza"},
        }

        result = get_ai_prefill_from_session(request)

        self.assertEqual(result, {"title": "Pizza"})
        self.assertNotIn("ai_recipe_prefill", request.session)


class StoreAIDietaryInfoTests(TestCase):
    def test_does_nothing_if_key_missing(self):
        session = {}
        ai_prefill = {}

        store_ai_dietary_info(session, ai_prefill)

        self.assertEqual(session, {})

    def test_stores_dietary_info(self):
        session = {}
        ai_prefill = {"ai_dietary_info": ["Vegan"]}

        store_ai_dietary_info(session, ai_prefill)

        self.assertEqual(session["ai_dietary_info"], ["Vegan"])
