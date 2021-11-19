import unittest
from mock import patch, Mock

from formica import cli
from tests.unit.constants import REGION, PROFILE, STACK, EVENT_ID, STACK_ID, ROLE_ARN


def test_rollback_stack(change_set, session, loader, stack_waiter, client):
    client.describe_stacks.return_value = {'Stacks': [{'StackId': STACK_ID}]}
    session.return_value.client.return_value = client
    client.describe_stack_events.return_value = {'StackEvents': [{'EventId': EVENT_ID}]}

    cli.main(['rollback', '--stack', STACK, '--profile', PROFILE, '--region', REGION])
    client.describe_stacks.assert_called_with(StackName=STACK)
    client.describe_stack_events.assert_called_with(StackName=STACK)
    client.rollback_stack.assert_called_with(StackName=STACK)
    stack_waiter.assert_called_with(STACK_ID)
    stack_waiter.return_value.wait.assert_called_with(EVENT_ID)


def test_rollback_stack_with_role(change_set, session, loader, stack_waiter, client):
    client.describe_stacks.return_value = {'Stacks': [{'StackId': STACK_ID}]}
    client.describe_stack_events.return_value = {'StackEvents': [{'EventId': EVENT_ID}]}

    cli.main(['rollback', '--stack', STACK, '--profile', PROFILE, '--region', REGION, '--role-arn', ROLE_ARN])
    client.describe_stacks.assert_called_with(StackName=STACK)
    client.describe_stack_events.assert_called_with(StackName=STACK)
    client.rollback_stack.assert_called_with(StackName=STACK, RoleARN=ROLE_ARN)
    stack_waiter.assert_called_with(STACK_ID)
    stack_waiter.return_value.wait.assert_called_with(EVENT_ID)
