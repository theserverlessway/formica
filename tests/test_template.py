import unittest
from unittest.mock import patch, mock_open

import os

import json

from formica import template


class TestTemplate(unittest.TestCase):

    @patch('formica.template.glob')
    def test_load_uses_current_path_as_default(self, glob):
        template.load()
        glob.glob.assert_called_with(f'{os.getcwd()}/*.fc')

    @patch('formica.template.glob')
    def test_load_uses_configured_path_and_module(self, glob):
        template.load('/some/path', 'module')
        glob.glob.assert_called_with('/some/path/module.fc')

    @patch('formica.template.compile')
    @patch('formica.template.exec')
    @patch('formica.template.open')
    @patch('formica.template.glob')
    def test_opens_globbed_files(self, glob, open, exec, compile):
        glob.glob.return_value = ['some-file']
        template.load('/some/path', 'module')
        open.assert_called_with('some-file')

    @patch('builtins.open', mock_open(
        read_data='resource(s3.Bucket("TestName"))'))
    @patch('formica.template.glob')
    def test_successfully_adds_resources_to_template(self, glob):
        glob.glob.return_value = ['some-file']
        template.load('/some/path', 'module')
        expected = {'Resources': {'TestName': {'Type': 'AWS::S3::Bucket'}}}
        actual = json.loads(template.template.to_json())
        self.assertEqual(actual, expected)
