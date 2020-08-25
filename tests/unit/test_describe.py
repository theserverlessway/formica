import pytest
from mock import Mock

from formica import cli
from tests.unit.constants import STACK


def test_describes_change_set(boto_client, change_set):
    cli.main(['describe', '--stack', STACK])
    boto_client.assert_called_with('cloudformation')
    change_set.assert_called_with(stack=STACK)
    change_set.return_value.describe.assert_called_once()
