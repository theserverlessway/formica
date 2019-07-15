import pytest
from formica import cli
from tests.unit.constants import REGION, PROFILE, STACK, TEMPLATE, ROLE_ARN, ACCOUNT_ID
from botocore.exceptions import ClientError


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


def test_change_create_if_missing(change_set, client, loader):
    client.get_caller_identity.return_value = {'Account': ACCOUNT_ID}
    exception = ClientError(
        dict(Error={'Code': 'ValidationError', 'Message': 'Stack with id teststack does not exist'}), "DescribeStack")
    client.describe_stacks.side_effect = exception
    loader.return_value.template.return_value = TEMPLATE
    cli.main(['change', '--stack', STACK, '--create-missing'])
    change_set.assert_called_with(stack=STACK, client=client)
    change_set.return_value.create.assert_called_once_with(template=TEMPLATE, change_set_type='CREATE',
                                                           parameters={},
                                                           tags={}, capabilities=None, s3=False, resource_types=False,
                                                           role_arn=None)


def test_change_create_if_missing_exception_handling(change_set, client, loader):
    client.get_caller_identity.return_value = {'Account': ACCOUNT_ID}
    exception = ClientError(
        dict(Error={'Code': 'OtherError', 'Message': 'Stack with id teststack does not exist'}), "DescribeStack")
    client.describe_stacks.side_effect = exception
    loader.return_value.template.return_value = TEMPLATE
    with pytest.raises(SystemExit):
        cli.main(['change', '--stack', STACK, '--create-missing'])

    exception = ClientError(
        dict(Error={'Code': 'ValidationError', 'Message': 'Other Error Message'}), "DescribeStack")
    client.describe_stacks.side_effect = exception
    with pytest.raises(SystemExit):
        cli.main(['change', '--stack', STACK, '--create-missing'])
