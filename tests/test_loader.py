import json
import unittest
from unittest.mock import patch, mock_open

from formica import loader


def openpatch(string=''):
    return patch('builtins.open', mock_open(read_data=string))


@patch('formica.loader.glob')
class TestLoader(unittest.TestCase):
    def setUp(self):
        self.loader = loader.Loader()

    def test_load_uses_current_path_as_default(self, glob):
        self.loader.load()
        glob.glob.assert_called_with(f'./*.fc')

    def test_load_uses_configured_path_and_module(self, glob):
        self.loader.load('/some/path', 'module')
        glob.glob.assert_called_with('/some/path/module.fc')

    @patch('builtins.open', mock_open())
    def test_opens_globbed_files(self, glob):
        glob.glob.return_value = ['some-file']
        self.loader.load('/some/path', 'module')
        open.assert_called_with('some-file')

    @openpatch('resource(s3.Bucket("TestName"))')
    def test_successfully_adds_resources_to_template(self, glob):
        glob.glob.return_value = ['some-file']
        self.loader.load('/some/path', 'module')
        expected = {'Resources': {'TestName': {'Type': 'AWS::S3::Bucket'}}}
        actual = json.loads(self.loader.template())
        self.assertEqual(actual, expected)

    @openpatch('description("TestDescription")')
    def test_successfully_adds_description_to_template(self, glob):
        glob.glob.return_value = ['some-file']
        self.loader.load('/some/path', 'module')
        expected = {'Description': 'TestDescription', 'Resources': {}}
        actual = json.loads(self.loader.template())
        self.assertEqual(actual, expected)

    @openpatch('metadata({"key": "value", "key2": "value2"})')
    def test_successfully_adds_metadata_to_template(self, glob):
        glob.glob.return_value = ['some-file']
        self.loader.load('/some/path', 'module')
        expected = {
            'Metadata': {
                'key': 'value',
                'key2': 'value2'},
            'Resources': {}}
        actual = json.loads(self.loader.template())
        self.assertEqual(actual, expected)

    @openpatch('condition("Condition1", Equals(Ref("EnvType"), "prod"))')
    def test_successfully_adds_condition_to_template(self, glob):
        glob.glob.return_value = ['some-file']
        self.loader.load('/some/path', 'module')
        expected = {'Conditions': {'Condition1': {'Fn::Equals': [{'Ref': 'EnvType'}, 'prod']}}, 'Resources': {}}
        actual = json.loads(self.loader.template())
        self.assertEqual(actual, expected)

    @openpatch('mapping("RegionMap", {"us-east-1": {"AMI": "ami-7f418316"}})')
    def test_successfully_adds_mapping_to_template(self, glob):
        glob.glob.return_value = ['some-file']
        self.loader.load('/some/path', 'module')
        expected = {'Mappings': {'RegionMap': {
            'us-east-1': {"AMI": "ami-7f418316"}}}, 'Resources': {}}
        actual = json.loads(self.loader.template())
        self.assertEqual(actual, expected)

    @openpatch('parameter(Parameter("param", Type="String"))')
    def test_successfully_adds_parameter_to_template(self, glob):
        glob.glob.return_value = ['some-file']
        self.loader.load('/some/path', 'module')
        expected = {'Parameters': {'param': {'Type': 'String'}},
                    'Resources': {}}
        actual = json.loads(self.loader.template())
        self.assertEqual(actual, expected)

    @openpatch('output(Output("Output", Value="value"))')
    def test_successfully_adds_output_to_template(self, glob):
        glob.glob.return_value = ['some-file']
        self.loader.load('/some/path', 'module')
        expected = {'Outputs': {'Output': {'Value': 'value'}},
                    'Resources': {}}
        actual = json.loads(self.loader.template())
        self.assertEqual(actual, expected)
