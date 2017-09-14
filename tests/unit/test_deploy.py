import pytest
from mock import Mock

from botocore.exceptions import NoCredentialsError

from formica import cli
from tests.unit.constants import STACK, PROFILE, REGION, CHANGESETNAME, EVENT_ID


@pytest.fixture
def stack_waiter(mocker):
    return mocker.patch('formica.cli.StackWaiter')


@pytest.fixture
def logger(mocker):
    return mocker.patch('formica.cli.logger')


@pytest.fixture
def session(mocker):
    return mocker.patch('formica.aws.Session')


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


def test_gets_cloudformation_client(session, stack_waiter):
    cli.main(['deploy', '--stack', STACK, '--profile', PROFILE, '--region', REGION])
    session.return_value.client.assert_called_with('cloudformation')


def test_executes_change_set_and_waits(session, stack_waiter):
    cf_client_mock = Mock()
    session.return_value.client.return_value = cf_client_mock
    cf_client_mock.describe_stack_events.return_value = {'StackEvents': [{'EventId': EVENT_ID}]}

    cli.main(['deploy', '--stack', STACK, '--profile', PROFILE, '--region', REGION])
    cf_client_mock.describe_stack_events.assert_called_with(StackName=STACK)
    cf_client_mock.execute_change_set.assert_called_with(ChangeSetName=CHANGESETNAME, StackName=STACK)
    stack_waiter.assert_called_with(STACK, cf_client_mock)
    stack_waiter.return_value.wait.assert_called_with(EVENT_ID)
