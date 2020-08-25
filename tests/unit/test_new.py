import pytest

from formica import cli
from tests.unit.constants import REGION, PROFILE, STACK, TEMPLATE


def test_create_changeset_for_new_stack(change_set, client, loader):
    loader.return_value.template.return_value = TEMPLATE
    cli.main(['new', '--stack', STACK, '--profile', PROFILE, '--region', REGION])
    change_set.assert_called_with(stack=STACK)
    change_set.return_value.create.assert_called_once_with(template=TEMPLATE, change_set_type='CREATE',
                                                           parameters={}, tags={}, capabilities=None,
                                                           resource_types=False, role_arn=None, s3=False)
    change_set.return_value.describe.assert_called_once()


def test_new_uses_parameters_for_creation(change_set, client, loader):
    loader.return_value.template.return_value = TEMPLATE
    cli.main(['new', '--stack', STACK, '--parameters', 'A=B', 'C=D', '--profile', PROFILE, '--region', REGION, ])
    change_set.assert_called_with(stack=STACK)
    change_set.return_value.create.assert_called_once_with(template=TEMPLATE, change_set_type='CREATE',
                                                           parameters={'A': 'B', 'C': 'D'}, tags={},
                                                           capabilities=None, resource_types=False, role_arn=None,
                                                           s3=False)


def test_new_uses_tags_for_creation(change_set, client, loader):
    loader.return_value.template.return_value = TEMPLATE
    cli.main(['new', '--stack', STACK, '--tags', 'A=C', 'C=D', '--profile', PROFILE, '--region', REGION, ])
    change_set.assert_called_with(stack=STACK)
    change_set.return_value.create.assert_called_once_with(template=TEMPLATE, change_set_type='CREATE',
                                                           parameters={},
                                                           tags={'A': 'C', 'C': 'D'}, capabilities=None,
                                                           resource_types=False, role_arn=None, s3=False)


def test_new_tests_parameter_format(capsys):
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        cli.main(
            ['new', '--stack', STACK, '--parameters', 'A=B', '--profile', PROFILE, '--region', REGION, '--tags', 'CD'])

    out, err = capsys.readouterr()

    assert "needs to be in format KEY=VALUE" in err
    assert pytest_wrapped_e.value.code == 2


def test_new_uses_capabilities_for_creation(change_set, client, loader):
    loader.return_value.template.return_value = TEMPLATE
    cli.main(['new', '--stack', STACK, '--capabilities', 'A', 'B'])
    change_set.assert_called_with(stack=STACK)
    change_set.return_value.create.assert_called_once_with(template=TEMPLATE, change_set_type='CREATE',
                                                           parameters={},
                                                           tags={}, capabilities=['A', 'B'], resource_types=False,
                                                           role_arn=None, s3=False)
