import unittest
from mock import patch, Mock

from formica import cli
from tests.unit.constants import REGION, PROFILE, STACK, EVENT_ID, STACK_ID, ROLE_ARN


class TestRemove(unittest.TestCase):
    @patch('formica.stack_waiter.StackWaiter')
    @patch('formica.loader.Loader')
    @patch('boto3.session.Session')
    @patch('formica.change_set.ChangeSet')
    def test_removes_stack(self, change_set, session, loader, stack_waiter):
        client_mock = Mock()
        client_mock.describe_stacks.return_value = {'Stacks': [{'StackId': STACK_ID}]}
        session.return_value.client.return_value = client_mock
        client_mock.describe_stack_events.return_value = {'StackEvents': [{'EventId': EVENT_ID}]}

        cli.main(['remove', '--stack', STACK, '--profile', PROFILE, '--region', REGION])
        client_mock.describe_stacks.assert_called_with(StackName=STACK)
        client_mock.describe_stack_events.assert_called_with(StackName=STACK)
        client_mock.delete_stack.assert_called_with(StackName=STACK)
        stack_waiter.assert_called_with(STACK_ID, client_mock)
        stack_waiter.return_value.wait.assert_called_with(EVENT_ID)

    @patch('formica.stack_waiter.StackWaiter')
    @patch('formica.loader.Loader')
    @patch('boto3.session.Session')
    @patch('formica.change_set.ChangeSet')
    def test_removes_stack_with_role(self, change_set, session, loader, stack_waiter):
        client_mock = Mock()
        client_mock.describe_stacks.return_value = {'Stacks': [{'StackId': STACK_ID}]}
        session.return_value.client.return_value = client_mock
        client_mock.describe_stack_events.return_value = {'StackEvents': [{'EventId': EVENT_ID}]}

        cli.main(['remove', '--stack', STACK, '--profile', PROFILE, '--region', REGION, '--role-arn', ROLE_ARN])
        client_mock.describe_stacks.assert_called_with(StackName=STACK)
        client_mock.describe_stack_events.assert_called_with(StackName=STACK)
        client_mock.delete_stack.assert_called_with(StackName=STACK, RoleARN=ROLE_ARN)
        stack_waiter.assert_called_with(STACK_ID, client_mock)
        stack_waiter.return_value.wait.assert_called_with(EVENT_ID)
