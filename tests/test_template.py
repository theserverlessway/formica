import unittest
from unittest.mock import patch, mock_open

import os

import json

from formica.template import Template


class TestTemplate(unittest.TestCase):

    def setUp(self):
        self.template = Template()

    @patch('formica.template.glob')
    def test_load_uses_current_path_as_default(self, glob):
        self.template.load()
        glob.glob.assert_called_with(f'{os.getcwd()}/*.fc')

    @patch('formica.template.glob')
    def test_load_uses_configured_path_and_module(self, glob):
        self.template.load('/some/path', 'module')
        glob.glob.assert_called_with('/some/path/module.fc')

    @patch('formica.template.compile')
    @patch('formica.template.exec')
    @patch('formica.template.open')
    @patch('formica.template.glob')
    def test_opens_globbed_files(self, glob, open, exec, compile):
        glob.glob.return_value = ['some-file']
        self.template.load('/some/path', 'module')
        open.assert_called_with('some-file')

    @patch('builtins.open', mock_open(
        read_data='resource(s3.Bucket("TestName"))'))
    @patch('formica.template.glob')
    def test_successfully_adds_resources_to_template(self, glob):
        glob.glob.return_value = ['some-file']
        self.template.load('/some/path', 'module')
        expected = {'Resources': {'TestName': {'Type': 'AWS::S3::Bucket'}}}
        actual = json.loads(self.template.template())
        self.assertEqual(actual, expected)

    @patch('builtins.open', mock_open(
        read_data='description("TestDescription")'))
    @patch('formica.template.glob')
    def test_successfully_adds_description_to_template(self, glob):
        glob.glob.return_value = ['some-file']
        self.template.load('/some/path', 'module')
        expected = {'Description': 'TestDescription', 'Resources': {}}
        actual = json.loads(self.template.template())
        self.assertEqual(actual, expected)

    @patch('builtins.open', mock_open(
        read_data='metadata({"key": "value", "key2": "value2"})'))
    @patch('formica.template.glob')
    def test_successfully_adds_metadata_to_template(self, glob):
        glob.glob.return_value = ['some-file']
        self.template.load('/some/path', 'module')
        expected = {'Metadata': {'key': 'value', 'key2': 'value2'}, 'Resources': {}}
        actual = json.loads(self.template.template())
        self.assertEqual(actual, expected)

    @patch('builtins.open', mock_open(
        read_data='condition("Condition1", Equals(Ref("EnvType"), "prod"))'))
    @patch('formica.template.glob')
    def test_successfully_adds_condition_to_template(self, glob):
        glob.glob.return_value = ['some-file']
        self.template.load('/some/path', 'module')
        expected = {'Conditions':
                    {'Condition1':
                        {'Fn::Equals':
                            [{'Ref': 'EnvType'}, 'prod']}}, 'Resources': {}}
        actual = json.loads(self.template.template())
        self.assertEqual(actual, expected)

    @patch('builtins.open', mock_open(
        read_data='mapping("RegionMap", {"us-east-1": {"AMI": "ami-7f418316"}})'))
    @patch('formica.template.glob')
    def test_successfully_adds_mapping_to_template(self, glob):
        glob.glob.return_value = ['some-file']
        self.template.load('/some/path', 'module')
        expected = {'Mappings':
            {'RegionMap': {'us-east-1': {"AMI": "ami-7f418316"}}}, 'Resources': {}}
        actual = json.loads(self.template.template())
        self.assertEqual(actual, expected)
