import unittest
import mock
from mock import patch, Mock

from click.testing import CliRunner

from formica import cli
from formica.cli import RESOURCE_HEADERS
from tests.unit.constants import STACK, LIST_STACK_RESOURCES


class TestResources(unittest.TestCase):
    def run_resources(self, exit_code=0):
        runner = CliRunner()
        result = runner.invoke(cli.resources, ['--stack', STACK])
        print(result.output)
        self.assertEqual(result.exit_code, exit_code)
        return result

    @patch('formica.cli.click')
    @patch('formica.aws.Session')
    def test_print_stacks(self, session, click):
        client_mock = Mock()
        session.return_value.client.return_value = client_mock
        client_mock.get_paginator.return_value.paginate.return_value = [LIST_STACK_RESOURCES]
        self.run_resources()

        client_mock.get_paginator.assert_called_with('list_stack_resources')
        client_mock.get_paginator.return_value.paginate.assert_called_with(StackName=STACK)

        click.echo.assert_called_with(mock.ANY)
        args = click.echo.call_args[0]

        to_search = []
        to_search.extend(RESOURCE_HEADERS)
        to_search.extend(['AWS::Route53::HostedZone'])
        to_search.extend(['FlomotlikMe'])
        to_search.extend(['CREATE_COMPLETE'])
        to_search.extend(['ZAYGDOKFPYFK6'])
        change_set_output = args[0]
        for term in to_search:
            self.assertIn(term, change_set_output)
        self.assertNotIn('None', change_set_output)
