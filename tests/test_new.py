import unittest
from unittest.mock import patch, Mock

from click.testing import CliRunner

from formica import cli
from tests.constants import REGION, PROFILE, STACK, TEMPLATE


class TestNew(unittest.TestCase):
    def run_create(self, exit_code=0):
        runner = CliRunner()
        result = runner.invoke(cli.new, ['--stack', STACK, '--profile', PROFILE, '--region', REGION])
        if result.exit_code != exit_code:
            print(result.output)
            print(result.exception)
            print(result.exit_code)
        self.assertEqual(result.exit_code, exit_code)
        return result

    @patch('formica.cli.Loader')
    @patch('formica.helper.AWSSession')
    @patch('formica.cli.ChangeSet')
    def test_create_changeset_for_new_stack(self, change_set, session, loader):
        client_mock = Mock()
        session.return_value.client_for.return_value = client_mock
        loader.return_value.template.return_value = TEMPLATE
        self.run_create()
        change_set.assert_called_with(stack=STACK, client=client_mock)
        change_set.return_value.create.assert_called_once_with(template=TEMPLATE, type='CREATE')
        change_set.return_value.describe.assert_called_once()
