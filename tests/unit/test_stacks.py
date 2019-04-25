import pytest
import mock
from mock import Mock

from formica import cli
from formica.cli import STACK_HEADERS
from tests.unit.constants import DESCRIBE_STACKS


def test_print_stacks(session, logger):
    client_mock = Mock()
    session.return_value.client.return_value = client_mock
    client_mock.describe_stacks.return_value = DESCRIBE_STACKS
    cli.main(['stacks'])

    logger.info.assert_called_with(mock.ANY)
    args = logger.info.call_args[0]

    to_search = []
    to_search.extend(STACK_HEADERS)
    to_search.extend(['teststack'])
    to_search.extend(['2017-01-31 11:51:43.596000'])
    to_search.extend(['2017-01-31 13:55:20.357000'])
    to_search.extend(['UPDATE_COMPLETE'])
    change_set_output = args[0]
    for term in to_search:
        assert term in change_set_output
    assert 'None' not in change_set_output


def test_does_not_fail_without_update_date(session, logger):
    client_mock = Mock()
    session.return_value.client.return_value = client_mock
    client_mock.describe_stacks.return_value = {
        "Stacks": [{'StackName': 'abc', 'CreationTime': '12345', 'StackStatus': 'status'}]
    }

    cli.main(['stacks'])
    logger.info.assert_called()
