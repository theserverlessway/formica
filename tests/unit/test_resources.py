import pytest
import mock
from mock import Mock

from formica import cli
from formica.cli import RESOURCE_HEADERS
from tests.unit.constants import STACK, LIST_STACK_RESOURCES


def test_print_stacks(session, logger):
    client_mock = Mock()
    session.return_value.client.return_value = client_mock
    client_mock.get_paginator.return_value.paginate.return_value = [LIST_STACK_RESOURCES]
    cli.main(['resources', '--stack', STACK])

    client_mock.get_paginator.assert_called_with('list_stack_resources')
    client_mock.get_paginator.return_value.paginate.assert_called_with(StackName=STACK)

    logger.info.assert_called_with(mock.ANY)
    args = logger.info.call_args[0]

    to_search = []
    to_search.extend(RESOURCE_HEADERS)
    to_search.extend(['AWS::Route53::HostedZone'])
    to_search.extend(['FlomotlikMe'])
    to_search.extend(['CREATE_COMPLETE'])
    to_search.extend(['ZAYGDOKFPYFK6'])
    change_set_output = args[0]
    for term in to_search:
        assert term in change_set_output
    assert 'None' not in change_set_output
