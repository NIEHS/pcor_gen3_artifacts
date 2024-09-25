import json
import unittest

from pcor_cedar.cedar_access import CedarAccess

class TestCedarAccess(unittest.TestCase):
    def test_retrieve_chords_folder_contents(self):
        cedar_access = CedarAccess()
        actual = cedar_access.retrieve_chords_folder_contents()
        self.assertIsNotNone(actual)

    def test_retrieve_resource(self):
        cedar_access = CedarAccess()
        actual = cedar_access.retrieve_resource("53884d98-4425-4276-98f8-fef46bc6534d")
        self.assertIsNotNone(actual)

    def test_retrieve_loading_folder(self):
        cedar_access = CedarAccess()
        actual = cedar_access.retrive_loading_contents()
        self.assertIsNotNone(actual)

    def test_parse_folder_contents(self):
        json_file = 'test_resources/loading_contents.json'
        cedar_access = CedarAccess()
        with open(json_file, 'r') as f:
            contents_json = json.loads(f.read())
            actual = cedar_access.parse_folder_listing(contents_json)
            self.assertIsNotNone(actual)



