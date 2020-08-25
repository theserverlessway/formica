import pytest
from mock import Mock

from formica import cli
from tests.unit.constants import STACK, STACK_ID, EVENT_ID


def test_cancel_stack_update(boto_client, aws_client, stack_waiter):
    aws_client.describe_stacks.return_value = {'Stacks': [{'StackId': STACK_ID}]}
    aws_client.describe_stack_events.return_value = {'StackEvents': [{'EventId': EVENT_ID}]}
    cli.main(['cancel', '--stack', STACK])
    boto_client.assert_called_with('cloudformation')
    aws_client.cancel_update_stack.assert_called_with(StackName=STACK)


def test_wait(aws_client, stack_waiter):
    aws_client.describe_stacks.return_value = {'Stacks': [{'StackId': STACK_ID}]}
    aws_client.describe_stack_events.return_value = {'StackEvents': [{'EventId': EVENT_ID}]}
    cli.main(['wait', '--stack', STACK])
