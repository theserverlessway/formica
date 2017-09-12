import pytest
from mock import Mock

from formica import cli
from tests.unit.constants import REGION, PROFILE, STACK, TEMPLATE


@pytest.fixture
def change_set(mocker):
    return mocker.patch('formica.cli.ChangeSet')


@pytest.fixture
def session(mocker):
    return mocker.patch('formica.aws.Session')


@pytest.fixture
def loader(mocker):
    return mocker.patch('formica.cli.Loader')


def test_create_changeset_for_new_stack(change_set, session, loader):
    client_mock = Mock()
    session.return_value.client.return_value = client_mock
    loader.return_value.template.return_value = TEMPLATE
    cli.main(['new', '--stack', STACK, '--profile', PROFILE, '--region', REGION])
    change_set.assert_called_with(stack=STACK, client=client_mock)
    change_set.return_value.create.assert_called_once_with(template=TEMPLATE, change_set_type='CREATE',
                                                           parameters=None, tags=None, capabilities=None)
    change_set.return_value.describe.assert_called_once()


def test_new_uses_parameters_for_creation(change_set, session, loader):
    client_mock = Mock()
    session.return_value.client.return_value = client_mock
    loader.return_value.template.return_value = TEMPLATE
    cli.main(['new', '--stack', STACK, '--parameters', 'A=B', 'C=D', '--profile', PROFILE, '--region', REGION])
    change_set.assert_called_with(stack=STACK, client=client_mock)
    change_set.return_value.create.assert_called_once_with(template=TEMPLATE, change_set_type='CREATE',
                                                           parameters=[{'A': 'B'}, {'C': 'D'}], tags=None,
                                                           capabilities=None)


def test_new_uses_tags_for_creation(change_set, session, loader):
    client_mock = Mock()
    session.return_value.client.return_value = client_mock
    loader.return_value.template.return_value = TEMPLATE
    cli.main(['new', '--stack', STACK, '--tags', 'A=B', 'C=D', '--profile', PROFILE, '--region', REGION])
    change_set.assert_called_with(stack=STACK, client=client_mock)
    change_set.return_value.create.assert_called_once_with(template=TEMPLATE, change_set_type='CREATE',
                                                           parameters=None,
                                                           tags=[{'A': 'B'}, {'C': 'D'}], capabilities=None)


def test_new_tests_parameter_format(capsys):
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        cli.main(['new', '--stack', STACK, '--parameters', 'A=B', 'CD', '--profile', PROFILE, '--region', REGION])
    assert pytest_wrapped_e.value.code == 2
    out, err = capsys.readouterr()
    assert 'needs to be in format KEY=VALUE' in err
    assert pytest_wrapped_e.value.code == 2


def test_new_uses_capabilities_for_creation(change_set, session, loader):
    client_mock = Mock()
    session.return_value.client.return_value = client_mock
    loader.return_value.template.return_value = TEMPLATE
    cli.main(['new', '--stack', STACK, '--capabilities', 'A', 'B'])
    change_set.assert_called_with(stack=STACK, client=client_mock)
    change_set.return_value.create.assert_called_once_with(template=TEMPLATE, change_set_type='CREATE',
                                                           parameters=None,
                                                           tags=None, capabilities=['A', 'B'])
