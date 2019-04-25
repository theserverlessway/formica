import pytest
from mock import Mock

from formica import cli
from tests.unit.constants import STACK, STACK_ID, EVENT_ID


@pytest.fixture
def client(mocker, session):
    client_mock = Mock()
    session.return_value.client.return_value = client_mock
    return client_mock


def test_cancel_stack_update(client, stack_waiter):
    client.describe_stacks.return_value = {'Stacks': [{'StackId': STACK_ID}]}
    client.describe_stack_events.return_value = {'StackEvents': [{'EventId': EVENT_ID}]}
    cli.main(['cancel', '--stack', STACK])
    client.cancel_update_stack.assert_called_with(StackName=STACK)


def test_wait(client, stack_waiter):
    client.describe_stacks.return_value = {'Stacks': [{'StackId': STACK_ID}]}
    client.describe_stack_events.return_value = {'StackEvents': [{'EventId': EVENT_ID}]}
    cli.main(['wait', '--stack', STACK])
