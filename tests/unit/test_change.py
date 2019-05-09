import pytest
from mock import Mock
from formica import cli
from tests.unit.constants import REGION, PROFILE, STACK, TEMPLATE, ROLE_ARN, ACCOUNT_ID


def test_change_creates_update_change_set(change_set, client, loader):
    loader.return_value.template.return_value = TEMPLATE
    cli.main(['change', '--stack', STACK, '--profile', PROFILE, '--region', REGION])
    change_set.assert_called_with(stack=STACK, client=client)
    change_set.return_value.create.assert_called_once_with(template=TEMPLATE, change_set_type='UPDATE',
                                                           parameters={},
                                                           tags={}, capabilities=None, role_arn=None, s3=False,
                                                           resource_types=False)
    change_set.return_value.describe.assert_called_once()


def test_change_uses_parameters_for_update(change_set, client, loader):
    loader.return_value.template.return_value = TEMPLATE
    cli.main(['change', '--stack', STACK, '--parameters', 'A=B', 'C=D', '--profile', PROFILE, '--region', REGION])
    change_set.assert_called_with(stack=STACK, client=client)
    change_set.return_value.create.assert_called_once_with(template=TEMPLATE, change_set_type='UPDATE',
                                                           parameters={'A': 'B', 'C': 'D'}, tags={},
                                                           capabilities=None, role_arn=None, s3=False,
                                                           resource_types=False)
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
                                                           parameters={}, tags={'A': 'B', 'C': 'D'},
                                                           capabilities=None, role_arn=None, s3=False,
                                                           resource_types=False)


def test_change_tests_tag_format(capsys):
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        cli.main(['change', '--stack', STACK, '--parameters', 'A=B', '--profile', PROFILE, '--region', REGION,
                  '--tags', 'CD'])
    out, err = capsys.readouterr()

    assert "argument --tags: CD needs to be in format KEY=VALUE" in err
    assert pytest_wrapped_e.value.code == 2


def test_change_uses_capabilities_for_creation(change_set, client, loader):
    loader.return_value.template.return_value = TEMPLATE
    cli.main(['change', '--stack', STACK, '--capabilities', 'A', 'B'])
    change_set.assert_called_with(stack=STACK, client=client)
    change_set.return_value.create.assert_called_once_with(template=TEMPLATE, change_set_type='UPDATE',
                                                           parameters={},
                                                           tags={}, capabilities=['A', 'B'], role_arn=None, s3=False,
                                                           resource_types=False)


def test_change_sets_s3_flag(change_set, client, loader):
    loader.return_value.template.return_value = TEMPLATE
    cli.main(['change', '--stack', STACK, '--s3'])
    change_set.assert_called_with(stack=STACK, client=client)
    change_set.return_value.create.assert_called_once_with(template=TEMPLATE, change_set_type='UPDATE',
                                                           parameters={},
                                                           tags={}, capabilities=None, role_arn=None, s3=True,
                                                           resource_types=False)


def test_change_with_role_arn(change_set, client, loader):
    loader.return_value.template.return_value = TEMPLATE
    cli.main(['change', '--stack', STACK, '--role-arn', ROLE_ARN])
    change_set.assert_called_with(stack=STACK, client=client)
    change_set.return_value.create.assert_called_once_with(template=TEMPLATE, change_set_type='UPDATE',
                                                           parameters={},
                                                           tags={}, capabilities=None, role_arn=ROLE_ARN, s3=False,
                                                           resource_types=False)


def test_change_with_role_name(change_set, client, loader):
    client.get_caller_identity.return_value = {'Account': ACCOUNT_ID}
    loader.return_value.template.return_value = TEMPLATE
    cli.main(['change', '--stack', STACK, '--role-name', 'some-stack-role'])
    change_set.assert_called_with(stack=STACK, client=client)
    change_set.return_value.create.assert_called_once_with(template=TEMPLATE, change_set_type='UPDATE',
                                                           parameters={},
                                                           tags={}, capabilities=None, role_arn=ROLE_ARN, s3=False,
                                                           resource_types=False)


def test_change_with_role_name_and_arn(change_set, client, loader):
    client.get_caller_identity.return_value = {'Account': ACCOUNT_ID}
    loader.return_value.template.return_value = TEMPLATE
    cli.main(['change', '--stack', STACK, '--role-name', 'UnusedRole', '--role-arn', ROLE_ARN])
    change_set.assert_called_with(stack=STACK, client=client)
    change_set.return_value.create.assert_called_once_with(template=TEMPLATE, change_set_type='UPDATE',
                                                           parameters={},
                                                           tags={}, capabilities=None, role_arn=ROLE_ARN, s3=False,
                                                           resource_types=False)


def test_change_with_resource_types(change_set, client, loader):
    client.get_caller_identity.return_value = {'Account': ACCOUNT_ID}
    loader.return_value.template.return_value = TEMPLATE
    cli.main(['change', '--stack', STACK, '--resource-types'])
    change_set.assert_called_with(stack=STACK, client=client)
    change_set.return_value.create.assert_called_once_with(template=TEMPLATE, change_set_type='UPDATE',
                                                           parameters={},
                                                           tags={}, capabilities=None, s3=False, resource_types=True,
                                                           role_arn=None)
