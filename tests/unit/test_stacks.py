import unittest
from unittest import mock
from unittest.mock import patch, Mock

from click.testing import CliRunner

from formica import cli
from formica.cli import STACK_HEADERS
from tests.unit.constants import DESCRIBE_STACKS


class TestStacks(unittest.TestCase):
    def run_stacks(self, exit_code=0):
        runner = CliRunner()
        result = runner.invoke(cli.stacks)
        self.assertEqual(result.exit_code, exit_code)
        return result

    @patch('formica.cli.click')
    @patch('formica.aws.Session')
    def test_print_stacks(self, session, click):
        client_mock = Mock()
        session.return_value.client.return_value = client_mock
        client_mock.describe_stacks.return_value = DESCRIBE_STACKS
        self.run_stacks()

        click.echo.assert_called_with(mock.ANY)
        args = click.echo.call_args[0]

        to_search = []
        to_search.extend(STACK_HEADERS)
        to_search.extend(['teststack'])
        to_search.extend(['2017-01-31 11:51:43.596000'])
        to_search.extend(['2017-01-31 13:55:20.357000'])
        to_search.extend(['UPDATE_COMPLETE'])
        change_set_output = args[0]
        for term in to_search:
            self.assertIn(term, change_set_output)
        self.assertNotIn('None', change_set_output)

    @patch('formica.cli.click')
    @patch('formica.aws.Session')
    def test_does_not_fail_without_update_date(self, session, click):
        client_mock = Mock()
        session.return_value.client.return_value = client_mock
        client_mock.describe_stacks.return_value = {
            "Stacks": [{'StackName': 'abc', 'CreationTime': '12345', 'StackStatus': 'status'}]
        }

        self.run_stacks()
        click.echo.assert_called()
