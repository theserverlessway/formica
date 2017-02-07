import unittest
from unittest.mock import patch, Mock

from click.testing import CliRunner

from formica import cli
from tests.constants import REGION, PROFILE, STACK, TEMPLATE


class TestChange(unittest.TestCase):
    @patch('formica.cli.Loader')
    @patch('formica.helper.AWSSession')
    @patch('formica.cli.ChangeSet')
    def test_change_creates_update_change_set(self, change_set, session, loader):
        client_mock = Mock()
        session.return_value.client_for.return_value = client_mock
        loader.return_value.template.return_value = TEMPLATE
        runner = CliRunner()
        result = runner.invoke(cli.change, ['--stack', STACK, '--profile', PROFILE, '--region', REGION])
        self.assertEqual(result.exit_code, 0)
        change_set.assert_called_with(stack=STACK, client=client_mock)
        change_set.return_value.create.assert_called_once_with(template=TEMPLATE, type='UPDATE', parameters={})
        change_set.return_value.describe.assert_called_once()

    @patch('formica.cli.Loader')
    @patch('formica.helper.AWSSession')
    @patch('formica.cli.ChangeSet')
    def test_change_uses_parameters_for_update(self, change_set, session, loader):
        client_mock = Mock()
        session.return_value.client_for.return_value = client_mock
        loader.return_value.template.return_value = TEMPLATE
        runner = CliRunner()
        result = runner.invoke(cli.change,
                               ['--stack', STACK, '--parameter', 'A=B', '--profile', PROFILE, '--region', REGION,
                                '--parameter', 'C=D'])
        self.assertEqual(result.exit_code, 0)
        change_set.assert_called_with(stack=STACK, client=client_mock)
        change_set.return_value.create.assert_called_once_with(template=TEMPLATE, type='UPDATE',
                                                               parameters={'A': 'B', 'C': 'D'})
        change_set.return_value.describe.assert_called_once()

    def test_change_tests_parameter_format(self):
        runner = CliRunner()
        result = runner.invoke(cli.change,
                               ['--stack', STACK, '--parameter', 'A=B', '--profile', PROFILE, '--region', REGION,
                                '--parameter', 'CD'])
        self.assertIn('parameters need to be in format KEY=VALUE', result.output)
        self.assertEqual(result.exit_code, 2)
