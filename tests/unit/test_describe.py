import sys
from unittest.mock import Mock

import pytest

from formica import cli
from tests.unit.constants import STACK


def test_describes_change_set(session, change_set):
    client_mock = Mock()
    session.return_value.client.return_value = client_mock
    cli.main(['describe', '--stack', STACK])
    session.return_value.client.assert_called_with('cloudformation')
    change_set.assert_called_with(stack=STACK, client=client_mock)
    if sys.version_info >= (3, 6):
        change_set.return_value.describe.assert_called_once()
    else:
        assert change_set.return_value.describe.call_count == 1
