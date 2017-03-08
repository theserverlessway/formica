import unittest
from mock import patch, Mock

from click.testing import CliRunner

from formica import cli
from tests.unit.constants import REGION, PROFILE, STACK, TEMPLATE


class TestChange(unittest.TestCase):
    @patch('formica.cli.Loader')
    @patch('formica.aws.Session')
    @patch('formica.cli.ChangeSet')
    def test_change_creates_update_change_set(self, change_set, session, loader):
        client_mock = Mock()
        session.return_value.client.return_value = client_mock
        loader.return_value.template.return_value = TEMPLATE
        runner = CliRunner()
        result = runner.invoke(cli.change, ['--stack', STACK, '--profile', PROFILE, '--region', REGION])
        self.assertEqual(result.exit_code, 0)
        change_set.assert_called_with(stack=STACK, client=client_mock)
        change_set.return_value.create.assert_called_once_with(template=TEMPLATE, change_set_type='UPDATE',
                                                               parameters={},
                                                               tags={}, capabilities=None)
        change_set.return_value.describe.assert_called_once()

    @patch('formica.cli.Loader')
    @patch('formica.aws.Session')
    @patch('formica.cli.ChangeSet')
    def test_change_uses_parameters_for_update(self, change_set, session, loader):
        client_mock = Mock()
        session.return_value.client.return_value = client_mock
        loader.return_value.template.return_value = TEMPLATE
        runner = CliRunner()
        result = runner.invoke(cli.change,
                               ['--stack', STACK, '--parameter', 'A=B', '--profile', PROFILE, '--region', REGION,
                                '--parameter', 'C=D'])
        self.assertEqual(result.exit_code, 0)
        change_set.assert_called_with(stack=STACK, client=client_mock)
        change_set.return_value.create.assert_called_once_with(template=TEMPLATE, change_set_type='UPDATE',
                                                               parameters={'A': 'B', 'C': 'D'}, tags={},
                                                               capabilities=None)
        change_set.return_value.describe.assert_called_once()

    def test_change_tests_parameter_format(self):
        runner = CliRunner()
        result = runner.invoke(cli.change,
                               ['--stack', STACK, '--parameter', 'A=B', '--profile', PROFILE, '--region', REGION,
                                '--parameter', 'CD'])
        self.assertIn('needs to be in format KEY=VALUE', result.output)
        self.assertEqual(result.exit_code, 2)

    @patch('formica.cli.Loader')
    @patch('formica.aws.Session')
    @patch('formica.cli.ChangeSet')
    def test_change_uses_tags_for_creation(self, change_set, session, loader):
        client_mock = Mock()
        session.return_value.client.return_value = client_mock
        loader.return_value.template.return_value = TEMPLATE
        runner = CliRunner()
        result = runner.invoke(cli.change,
                               ['--stack', STACK, '--tag', 'A=B', '--profile', PROFILE, '--region', REGION,
                                '--tag', 'C=D'])
        self.assertEqual(result.exit_code, 0)
        change_set.assert_called_with(stack=STACK, client=client_mock)
        change_set.return_value.create.assert_called_once_with(template=TEMPLATE, change_set_type='UPDATE',
                                                               parameters={},
                                                               tags={'A': 'B', 'C': 'D'}, capabilities=None)

    def test_change_tests_tag_format(self):
        runner = CliRunner()
        result = runner.invoke(cli.change,
                               ['--stack', STACK, '--parameter', 'A=B', '--profile', PROFILE, '--region', REGION,
                                '--tag', 'CD'])
        self.assertIn('needs to be in format KEY=VALUE', result.output)
        self.assertEqual(result.exit_code, 2)

    @patch('formica.cli.Loader')
    @patch('formica.aws.Session')
    @patch('formica.cli.ChangeSet')
    def test_change_uses_capabilities_for_creation(self, change_set, session, loader):
        client_mock = Mock()
        session.return_value.client.return_value = client_mock
        loader.return_value.template.return_value = TEMPLATE
        runner = CliRunner()
        result = runner.invoke(cli.change,
                               ['--stack', STACK, '--capabilities', 'A,B'])
        self.assertEqual(result.exit_code, 0)
        change_set.assert_called_with(stack=STACK, client=client_mock)
        change_set.return_value.create.assert_called_once_with(template=TEMPLATE, change_set_type='UPDATE',
                                                               parameters={},
                                                               tags={}, capabilities=['A', 'B'])
