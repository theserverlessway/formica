import unittest
from unittest.mock import patch, Mock

from click.testing import CliRunner

from formica import cli
from tests.constants import REGION, PROFILE, STACK, EVENT_ID, STACK_ID


class TestRemove(unittest.TestCase):
    def run_create(self, exit_code=0):
        runner = CliRunner()
        result = runner.invoke(cli.remove, ['--stack', STACK, '--profile', PROFILE, '--region', REGION])
        if result.exit_code != exit_code:
            print(result.output)
            print(result.exception)
            print(result.exit_code)
        self.assertEqual(result.exit_code, exit_code)
        return result

    @patch('formica.cli.StackWaiter')
    @patch('formica.cli.Loader')
    @patch('formica.helper.AWSSession')
    @patch('formica.cli.ChangeSet')
    def test_removes_stack(self, change_set, session, loader, stack_waiter):
        client_mock = Mock()
        client_mock.describe_stacks.return_value = {'Stacks': [{'StackId': STACK_ID}]}
        session.return_value.client_for.return_value = client_mock
        client_mock.describe_stack_events.return_value = {'StackEvents': [{'EventId': EVENT_ID}]}

        self.run_create()
        client_mock.describe_stacks.assert_called_with(StackName=STACK)
        client_mock.describe_stack_events.assert_called_with(StackName=STACK)
        client_mock.delete_stack.assert_called_with(StackName=STACK)
        stack_waiter.assert_called_with(STACK_ID, client_mock)
        stack_waiter.return_value.wait.assert_called_with(EVENT_ID)

