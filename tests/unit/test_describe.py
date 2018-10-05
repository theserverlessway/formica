import pytest
from mock import Mock

from formica import cli
from tests.unit.constants import STACK


@pytest.fixture
def change_set(mocker):
    return mocker.patch('formica.change_set.ChangeSet')


@pytest.fixture
def session(mocker):
    return mocker.patch('boto3.session.Session')


def test_describes_change_set(session, change_set):
    client_mock = Mock()
    session.return_value.client.return_value = client_mock
    cli.main(['describe', '--stack', STACK])
    session.return_value.client.assert_called_with('cloudformation')
    change_set.assert_called_with(stack=STACK, client=client_mock)
    change_set.return_value.describe.assert_called_once()
