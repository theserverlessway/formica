import pytest
from mock import Mock
from datetime import datetime, timedelta

from formica.stack_waiter import StackWaiter, EVENT_TABLE_HEADERS
from tests.unit.constants import STACK, STACK_EVENTS


@pytest.fixture
def time(mocker):
    return mocker.patch('formica.stack_waiter.time')


@pytest.fixture
def datetime_mock(mocker):
    return mocker.patch('formica.stack_waiter.datetime')


@pytest.fixture
def logger(mocker):
    return mocker.patch('formica.stack_waiter.logger')


@pytest.fixture
def stack_waiter():
    return StackWaiter(STACK)

@pytest.fixture
def client(mocker):
    client = mocker.patch('formica.stack_waiter.cf')
    return client

def set_stack_status_returns(client, statuses):
    client.describe_stacks.side_effect = [{'Stacks': [{'StackStatus': status}]} for status in
                                                  statuses]


def set_stack_events(client, events=1):
    stack_events = {'StackEvents': [{"EventId": str(num)} for num in range(events)]}
    client.describe_stack_events.return_value = stack_events


def test_prints_header(time, mocker, client, stack_waiter):
    header = mocker.patch.object(StackWaiter, 'print_header')
    set_stack_status_returns(client, ['CREATE_COMPLETE'])
    client.describe_stack_events.return_value = STACK_EVENTS
    stack_waiter.wait('DeploymentBucket3-7c92066b-c2e7-427a-ab29-53b928925473')
    header.assert_called()


def test_waits_until_successful(client, time, stack_waiter):
    set_stack_status_returns(client, ['UPDATE_IN_PROGRESS', 'CREATE_COMPLETE'])
    set_stack_events(client)
    stack_waiter.wait('0')
    assert time.sleep.call_count == 1
    time.sleep.assert_called_with(5)


def test_waits_until_failed_and_raises(client, time, stack_waiter):
    set_stack_status_returns(client, ['UPDATE_IN_PROGRESS', 'CREATE_FAILED'])
    set_stack_events(client)
    with pytest.raises(SystemExit, match='1'):
        stack_waiter.wait('0')
    assert time.sleep.call_count == 1


def test_waits_until_timeout(client, time, datetime_mock):
    first_timestamp = datetime.now()
    second_timestamp = datetime.now() + timedelta(0, 50, 0)
    last_timestamp = datetime.now() + timedelta(0, 61, 0)
    datetime_mock.now.side_effect = [first_timestamp, second_timestamp, last_timestamp]
    set_stack_status_returns(client,
                             ['UPDATE_IN_PROGRESS', 'UPDATE_IN_PROGRESS', 'UPDATE_IN_PROGRESS', 'CREATE_FAILED'])
    set_stack_events(client)
    stack_waiter = StackWaiter(STACK, timeout=1)
    with pytest.raises(SystemExit, match='1'):
        stack_waiter.wait('0')
    assert time.sleep.call_count == 2
    client.cancel_update_stack.assert_called_with(StackName=STACK)


def test_prints_new_events(logger, time, client, stack_waiter):
    set_stack_status_returns(client, ['CREATE_COMPLETE'])
    client.describe_stack_events.return_value = STACK_EVENTS
    stack_waiter.wait('DeploymentBucket3-7c92066b-c2e7-427a-ab29-53b928925473')

    logger.info.assert_called()
    output = '\n'.join([call[1][0] for call in logger.info.mock_calls])
    to_search = []
    to_search.extend(EVENT_TABLE_HEADERS)
    to_search.extend(['UPDATE_COMPLETE', 'DELETE_COMPLETE'])
    to_search.extend(['AWS::S3::Bucket', 'AWS::CloudFormation::Stack'])
    to_search.extend(['2017-02-06 16:01:16', '2017-02-06 16:01:16', '2017-02-06 16:01:17'])
    to_search.extend(['DeploymentBucket14', 'DeploymentBucket18', 'teststack '])
    to_search.extend(['Resource creation Initiated'])
    for term in to_search:
        assert term in output

    old_events = ['DeploymentBucket3', 'DeploymentBucket15']
    for term in old_events:
        assert term not in output
    assert 'None' not in output
