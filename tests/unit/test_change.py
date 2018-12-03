import pytest
from mock import Mock
from formica import cli
from tests.unit.constants import REGION, PROFILE, STACK, TEMPLATE, ROLE_ARN, ACCOUNT_ID


@pytest.fixture
def change_set(mocker):
    return mocker.patch('formica.change_set.ChangeSet')


@pytest.fixture
def session(mocker):
    return mocker.patch('boto3.session.Session')


@pytest.fixture
def client(session):
    client_mock = Mock()
    session.return_value.client.return_value = client_mock
    return client_mock


@pytest.fixture
def loader(mocker):
    return mocker.patch('formica.loader.Loader')


def test_change_creates_update_change_set(change_set, client, loader):
    print(client)
    loader.return_value.template.return_value = TEMPLATE
    cli.main(['change', '--stack', STACK, '--profile', PROFILE, '--region', REGION])
    change_set.assert_called_with(stack=STACK, client=client)
    change_set.return_value.create.assert_called_once_with(template=TEMPLATE, change_set_type='UPDATE',
                                                           parameters=None,
                                                           tags=None, capabilities=None, role_arn=None, s3=False)
    change_set.return_value.describe.assert_called_once()


def test_change_uses_parameters_for_update(change_set, client, loader):
    loader.return_value.template.return_value = TEMPLATE
    cli.main(['change', '--stack', STACK, '--parameters', 'A=B', 'C=D', '--profile', PROFILE, '--region', REGION])
    change_set.assert_called_with(stack=STACK, client=client)
    change_set.return_value.create.assert_called_once_with(template=TEMPLATE, change_set_type='UPDATE',
                                                           parameters={'A': 'B', 'C': 'D'}, tags=None,
                                                           capabilities=None, role_arn=None, s3=False)
    change_set.return_value.describe.assert_called_once()


def test_change_tests_parameter_format(capsys):
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        cli.main(['change', '--stack', STACK, '--parameter', 'A=B', 'CD', '--profile', PROFILE, '--region', REGION])
    out, err = capsys.readouterr()
    assert 'needs to be in format KEY=VALUE' in err
    assert pytest_wrapped_e.value.code == 2


def test_change_uses_tags_for_creation(change_set, client, loader):
    loader.return_value.template.return_value = TEMPLATE
    cli.main(['change', '--stack', STACK, '--tags', 'A=B', 'C=D', '--profile', PROFILE, '--region', REGION])
    change_set.assert_called_with(stack=STACK, client=client)
    change_set.return_value.create.assert_called_once_with(template=TEMPLATE, change_set_type='UPDATE',
                                                           parameters=None, tags={'A': 'B', 'C': 'D'},
                                                           capabilities=None, role_arn=None, s3=False)


def test_change_tests_tag_format(capsys):
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        cli.main(['change', '--stack', STACK, '--parameters', 'A=B', '--profile', PROFILE, '--region', REGION,
                  '--tags', 'CD'])
    out, err = capsys.readouterr()
    assert "argument --tags: 'CD' needs to be in format KEY=VALUE" in err
    assert pytest_wrapped_e.value.code == 2


def test_change_uses_capabilities_for_creation(change_set, client, loader):
    loader.return_value.template.return_value = TEMPLATE
    cli.main(['change', '--stack', STACK, '--capabilities', 'A', 'B'])
    change_set.assert_called_with(stack=STACK, client=client)
    change_set.return_value.create.assert_called_once_with(template=TEMPLATE, change_set_type='UPDATE',
                                                           parameters=None,
                                                           tags=None, capabilities=['A', 'B'], role_arn=None, s3=False)


def test_change_sets_s3_flag(change_set, client, loader):
    loader.return_value.template.return_value = TEMPLATE
    cli.main(['change', '--stack', STACK, '--s3'])
    change_set.assert_called_with(stack=STACK, client=client)
    change_set.return_value.create.assert_called_once_with(template=TEMPLATE, change_set_type='UPDATE',
                                                           parameters=None,
                                                           tags=None, capabilities=None, role_arn=None, s3=True)


def test_change_with_role_arn(change_set, client, loader):
    loader.return_value.template.return_value = TEMPLATE
    cli.main(['change', '--stack', STACK, '--role-arn', ROLE_ARN])
    change_set.assert_called_with(stack=STACK, client=client)
    change_set.return_value.create.assert_called_once_with(template=TEMPLATE, change_set_type='UPDATE',
                                                           parameters=None,
                                                           tags=None, capabilities=None, role_arn=ROLE_ARN, s3=False)


def test_change_with_role_name(change_set, client, loader):
    client.get_caller_identity.return_value = {'Account': ACCOUNT_ID}
    loader.return_value.template.return_value = TEMPLATE
    cli.main(['change', '--stack', STACK, '--role-name', 'some-stack-role'])
    change_set.assert_called_with(stack=STACK, client=client)
    change_set.return_value.create.assert_called_once_with(template=TEMPLATE, change_set_type='UPDATE',
                                                           parameters=None,
                                                           tags=None, capabilities=None, role_arn=ROLE_ARN, s3=False)


def test_change_with_role_name_and_arn(change_set, client, loader):
    client.get_caller_identity.return_value = {'Account': ACCOUNT_ID}
    loader.return_value.template.return_value = TEMPLATE
    cli.main(['change', '--stack', STACK, '--role-name', 'UnusedRole', '--role-arn', ROLE_ARN])
    change_set.assert_called_with(stack=STACK, client=client)
    change_set.return_value.create.assert_called_once_with(template=TEMPLATE, change_set_type='UPDATE',
                                                           parameters=None,
                                                           tags=None, capabilities=None, role_arn=ROLE_ARN, s3=False)
