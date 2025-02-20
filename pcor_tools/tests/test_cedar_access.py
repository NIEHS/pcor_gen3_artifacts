import json
import unittest

from pcor_cedar.loader_cedar import LoaderCedar
from pcor_cedar.cedar_access import CedarAccess

class TestCedarAccess(unittest.TestCase):
    def test_retrieve_chords_folder_contents(self):
        cedar_access = CedarAccess()
        actual = cedar_access.retrieve_chords_folder_contents()
        self.assertIsNotNone(actual)

    def test_retrieve_resource(self):
        cedar_access = CedarAccess()
        actual = cedar_access.retrieve_resource("https://repo.metadatacenter.org/template-instances/53884d98-4425-4276-98f8-fef46bc6534d")
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

    def test_create_resource(self):
        cedar_access = CedarAccess()
        resource_json = cedar_access.produce_geoexposure_json({})
        actual = cedar_access.create_resource(resource_json)
        self.assertIsNotNone(actual)

    def test_rename_resource(self):
        cedar_access = CedarAccess()
        test_id = "https://cedar.metadatacenter.org/instances/edit/https://repo.metadatacenter.org/template-instances/72db6bb6-b626-4624-97f2-12bb9b714281?folderId=https:%2F%2Frepo.metadatacenter.org%2Ffolders%2F37c3bdd7-d006-4cc5-8a0a-46e7c256cd95"
        id = LoaderCedar.extract_id_for_resource(test_id)
        name = "test name - renamed2"
        cedar_access.rename_resource(id, name)

    def test_retrieve_folder_contents(self):
        cedar_access = CedarAccess()
        working_dir = cedar_access.cedar_config.cedar_properties['working_directory']
        input_folder = cedar_access.cedar_config.cedar_properties['cedar_folder']
        actual = cedar_access.retrieve_folder_contents(input_folder)
        self.assertIsNotNone(actual)

