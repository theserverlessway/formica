import pytest
from mock import Mock

from botocore.exceptions import NoCredentialsError

from formica import cli
from tests.unit.constants import STACK, STACK_ID, PROFILE, REGION, CHANGESETNAME, EVENT_ID


@pytest.fixture
def stack_waiter(mocker):
    return mocker.patch('formica.stack_waiter.StackWaiter')


@pytest.fixture
def logger(mocker):
    return mocker.patch('formica.cli.logger')


@pytest.fixture
def session(mocker):
    return mocker.patch('boto3.session.Session')


def test_catches_common_aws_exceptions(session, stack_waiter):
    session.side_effect = NoCredentialsError()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        cli.main(['deploy', '--stack', STACK])
    assert pytest_wrapped_e.value.code == 1


def test_fails_if_no_stack_given(logger):
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        cli.main(['deploy'])
    assert pytest_wrapped_e.value.code == 1

    logger.error.assert_called()
    out = logger.error.call_args[0][0]
    assert '--stack' in out
    assert '--config-file' in out


def test_executes_change_set_and_waits(session, stack_waiter, client):
    client.describe_change_set.return_value = {'Status': 'CREATE_COMPLETE'}
    client.describe_stack_events.return_value = {'StackEvents': [{'EventId': EVENT_ID}]}
    client.describe_stacks.return_value = {'Stacks': [{'StackId': STACK_ID}]}

    cli.main(['deploy', '--stack', STACK, '--profile', PROFILE, '--region', REGION])
    session.return_value.client.assert_called_with('cloudformation')
    client.describe_stack_events.assert_called_with(StackName=STACK)
    client.execute_change_set.assert_called_with(ChangeSetName=CHANGESETNAME, StackName=STACK)
    client.describe_change_set.assert_called_with(ChangeSetName=CHANGESETNAME, StackName=STACK)
    stack_waiter.assert_called_with(STACK_ID, client)
    stack_waiter.return_value.wait.assert_called_with(EVENT_ID)


def test_executes_change_set_with_timeout(stack_waiter, client):
    client.describe_change_set.return_value = {'Status': 'CREATE_COMPLETE'}
    client.describe_stack_events.return_value = {'StackEvents': [{'EventId': EVENT_ID}]}
    client.describe_stacks.return_value = {'Stacks': [{'StackId': STACK_ID}]}

    cli.main(['deploy', '--stack', STACK, '--profile', PROFILE, '--region', REGION, '--timeout', '15'])
    stack_waiter.assert_called_with(STACK_ID, client, timeout=15)
    stack_waiter.return_value.wait.assert_called_with(EVENT_ID)


def test_does_not_execute_changeset_if_no_changes(stack_waiter, client):
    print(client)
    client.describe_change_set.return_value = {'Status': 'FAILED',
                                               "StatusReason": "The submitted information didn't contain changes. Submit different information to create a change set."}
    client.describe_stack_events.return_value = {'StackEvents': [{'EventId': EVENT_ID}]}
    client.describe_stacks.return_value = {'Stacks': [{'StackId': STACK_ID}]}

    cli.main(['deploy', '--stack', STACK])
    client.execute_change_set.assert_not_called()
    stack_waiter.assert_called_with(STACK_ID, client)
    stack_waiter.return_value.wait.assert_called_with(EVENT_ID)


def test_does_not_execute_changeset_if_in_failed_state(stack_waiter, client):
    client.describe_change_set.return_value = {'Status': 'FAILED'}
    client.describe_stack_events.return_value = {'StackEvents': [{'EventId': EVENT_ID}]}
    client.describe_stacks.return_value = {'Stacks': [{'StackId': STACK_ID}]}

    with pytest.raises(SystemExit):
        cli.main(['deploy', '--stack', STACK])
    client.execute_change_set.assert_not_called()
