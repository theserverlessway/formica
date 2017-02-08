import unittest
from unittest.mock import patch, Mock

from click.testing import CliRunner

from formica import cli
from tests.constants import STACK


class TestDescribe(unittest.TestCase):
    def run_describe(self, exit_code=0):
        runner = CliRunner()
        result = runner.invoke(cli.describe, ['--stack', STACK])
        if result.exit_code != exit_code:
            print(result.output)
            print(result.exception)
            print(result.exit_code)
        self.assertEqual(result.exit_code, exit_code)
        return result

    @patch('formica.cli.ChangeSet')
    @patch('formica.helper.AWSSession')
    def test_describes_change_set(self, session, change_set):
        client_mock = Mock()
        session.return_value.client_for.return_value = client_mock
        self.run_describe()
        session.return_value.client_for.assert_called_with('cloudformation')
        change_set.assert_called_with(stack=STACK, client=client_mock)
        change_set.return_value.describe.assert_called_once()
