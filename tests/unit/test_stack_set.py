import pytest
import json
from uuid import uuid4

from formica import cli, stack_set
from tests.unit.constants import STACK, CLOUDFORMATION_PARAMETERS, CLOUDFORMATION_TAGS
from tests.unit.constants import TEMPLATE, EC2_REGIONS, ACCOUNTS, ACCOUNT_ID

from path import Path


@pytest.fixture
def logger(mocker):
    return mocker.patch('formica.stack_set.logger')


@pytest.fixture
def session(mocker):
    return mocker.patch('boto3.session.Session')


@pytest.fixture
def client(session, mocker):
    client_mock = mocker.Mock()
    session.return_value.client.return_value = client_mock
    return client_mock


@pytest.fixture
def loader(mocker):
    mock = mocker.patch('formica.loader.Loader')
    mock.return_value.template.return_value = TEMPLATE
    return mock


@pytest.fixture
def template(client, mocker):
    template = mocker.Mock()
    client.describe_stack_set.return_value = {'StackSet': {'TemplateBody': template}}
    return template


def dump_template(template):
    return json.dumps(template, indent=None, sort_keys=True, separators=(',', ':'))


def test_create_stack_set(client, logger, loader):
    cli.main([
        'stack-set',
        'create',
        '--stack-set', STACK,
        '--parameters', 'A=B', 'B=C',
        '--tags', 'A=B', 'B=C',
        '--capabilities', 'CAPABILITY_IAM',
        '--execution-role-name', 'ExecutionRole',
        '--administration-role-arn', 'AdministrationRole',
    ])

    client.create_stack_set.assert_called_with(
        StackSetName=STACK,
        TemplateBody=TEMPLATE,
        Parameters=CLOUDFORMATION_PARAMETERS,
        Tags=CLOUDFORMATION_TAGS,
        Capabilities=['CAPABILITY_IAM'],
        ExecutionRoleName='ExecutionRole',
        AdministrationRoleARN='AdministrationRole'
    )


def test_create_stack_set_with_administration_name(client, logger, loader):
    client.get_caller_identity.return_value = {'Account': ACCOUNT_ID}
    cli.main([
        'stack-set',
        'create',
        '--stack-set', STACK,
        '--administration-role-name', 'AdministrationRole',
    ])

    client.create_stack_set.assert_called_with(
        StackSetName=STACK,
        TemplateBody=TEMPLATE,
        AdministrationRoleARN='arn:aws:iam::1234567890:role/AdministrationRole'
    )


def test_create_stack_set_without_arguments(client, logger, loader):
    cli.main([
        'stack-set',
        'create',
        '--stack-set', STACK
    ])

    client.create_stack_set.assert_called_with(
        StackSetName=STACK,
        TemplateBody=TEMPLATE
    )


def test_create_stack_set_with_main_account(session, client, logger, tmpdir):
    accountid = str(uuid4())
    client.get_caller_identity.return_value = {'Account': accountid}
    with Path(tmpdir):
        with open('test.template.json', 'w') as f:
            f.write('')
        cli.main([
            'stack-set',
            'create',
            '--stack-set', STACK,
            '--main-account-parameter'
        ])

    session.return_value.client.assert_called_with('sts')

    client.create_stack_set.assert_called_with(
        StackSetName=STACK,
        TemplateBody=dump_template({'Parameters': {'MainAccount': {'Type': 'String', 'Default': accountid}}})
    )


def test_create_stack_set_with_main_account_and_existing_parameters(session, client, logger, tmpdir):
    accountid = str(uuid4())
    client.get_caller_identity.return_value = {'Account': accountid}
    with Path(tmpdir):
        with open('test.template.json', 'w') as f:
            f.write(json.dumps({'Parameters': {'SomeParam': {'Type': 'String'}}}))
        cli.main([
            'stack-set',
            'create',
            '--stack-set', STACK,
            '--main-account-parameter',
            '--parameters', 'A=B'

        ])

    client.create_stack_set.assert_called_with(
        StackSetName=STACK,
        TemplateBody=dump_template(
            {'Parameters': {'SomeParam': {'Type': 'String'}, 'MainAccount': {'Type': 'String', 'Default': accountid}}}),
        Parameters=[{'ParameterKey': 'A', 'ParameterValue': 'B', 'UsePreviousValue': False}]
    )


def test_update_stack_set(client, loader):
    client.update_stack_set.return_value = {'OperationId': '12345'}

    cli.main([
        'stack-set',
        'update',
        '--stack-set', STACK,
        '--parameters', 'A=B', 'B=C',
        '--tags', 'A=B', 'B=C',
        '--capabilities', 'CAPABILITY_IAM',
        '--execution-role-name', 'ExecutionRole',
        '--administration-role-arn', 'AdministrationRole',
        '--accounts', '123456789', '987654321',
        '--regions', 'eu-central-1', 'eu-west-1',
        '--region-order', 'eu-central-1', 'eu-west-1',
        '--failure-tolerance-count', '1',
        '--max-concurrent-count', '1'
    ])

    client.update_stack_set.assert_called_with(
        StackSetName=STACK,
        TemplateBody=TEMPLATE,
        Parameters=CLOUDFORMATION_PARAMETERS,
        Tags=CLOUDFORMATION_TAGS,
        Capabilities=['CAPABILITY_IAM'],
        ExecutionRoleName='ExecutionRole',
        AdministrationRoleARN='AdministrationRole',
        Accounts=['123456789', '987654321'],
        Regions=['eu-central-1', 'eu-west-1'],
        OperationPreferences={
            'RegionOrder': ['eu-central-1', 'eu-west-1'],
            'FailureToleranceCount': 1,
            'MaxConcurrentCount': 1
        }
    )


def test_update_stack_set_with_main_account(session, client, logger, mocker, tmpdir):
    client.update_stack_set.return_value = {'OperationId': '12345'}
    accountid = str(uuid4())
    client.get_caller_identity.return_value = {'Account': accountid}
    with Path(tmpdir):
        with open('test.template.json', 'w') as f:
            f.write('')
        cli.main([
            'stack-set',
            'update',
            '--stack-set', STACK,
            '--main-account-parameter'
        ])

    session.return_value.client.assert_any_call('sts')
    session.return_value.client.assert_any_call('cloudformation')

    client.update_stack_set.assert_called_with(
        StackSetName=STACK,
        TemplateBody=dump_template({'Parameters': {'MainAccount': {'Type': 'String', 'Default': accountid}}})
    )


def test_update_stack_set_with_all_regions_and_accounts(client, logger, loader):
    client.update_stack_set.return_value = {'OperationId': '12345'}
    client.get_caller_identity.return_value = {'Account': '5678'}
    client.list_accounts.return_value = ACCOUNTS
    client.describe_regions.return_value = EC2_REGIONS
    cli.main([
        'stack-set',
        'update',
        '--stack-set', STACK,
        '--all-regions',
        '--all-accounts'
    ])

    client.update_stack_set.assert_called_with(
        StackSetName=STACK,
        TemplateBody=TEMPLATE,
        Accounts=['1234', '5678'],
        Regions=['us-west-1', 'us-west-2']
    )


def test_update_stack_set_with_all_subaccounts(client, logger, loader):
    client.update_stack_set.return_value = {'OperationId': '12345'}
    client.list_accounts.return_value = ACCOUNTS
    client.get_caller_identity.return_value = {'Account': '5678'}
    client.describe_regions.return_value = EC2_REGIONS
    cli.main([
        'stack-set',
        'update',
        '--stack-set', STACK,
        '--all-subaccounts'
    ])

    client.update_stack_set.assert_called_with(
        StackSetName=STACK,
        TemplateBody=TEMPLATE,
        Accounts=['1234']
    )


def test_add_stack_set_instances(client, loader):
    cli.main([
        'stack-set',
        'add-instances',
        '--stack-set', STACK,
        '--accounts', '123456789', '987654321',
        '--regions', 'eu-central-1', 'eu-west-1',
    ])

    client.create_stack_instances.assert_called_with(
        StackSetName=STACK,
        Accounts=['123456789', '987654321'],
        Regions=['eu-central-1', 'eu-west-1']
    )


def test_stack_set_accounts_converts_to_string():
    assert stack_set.accounts({'accounts': ['123', 12345, 54321]}) == ['123', '12345', '54321']


def test_add_all_stack_set_instances(client, loader):
    client.list_accounts.return_value = ACCOUNTS
    client.get_caller_identity.return_value = {'Account': '5678'}
    client.describe_regions.return_value = EC2_REGIONS
    cli.main([
        'stack-set',
        'add-instances',
        '--stack-set', STACK,
        '--all-accounts',
        '--all-regions',
    ])

    client.create_stack_instances.assert_called_with(
        StackSetName=STACK,
        Accounts=['1234', '5678'],
        Regions=['us-west-1', 'us-west-2']
    )


def test_add_stack_set_instances_with_operation_preferences(client, loader):
    cli.main([
        'stack-set',
        'add-instances',
        '--accounts', '123456789', '987654321',
        '--regions', 'eu-central-1', 'eu-west-1',
        '--stack-set', STACK,
        '--max-concurrent-percentage', '1',
        '--failure-tolerance-percentage', '1',
    ])

    client.create_stack_instances.assert_called_with(
        StackSetName=STACK,
        Accounts=['123456789', '987654321'],
        Regions=['eu-central-1', 'eu-west-1'],
        OperationPreferences={
            'FailureTolerancePercentage': 1,
            'MaxConcurrentPercentage': 1
        }
    )


def test_remove_stack_set_instances(client, loader):
    cli.main([
        'stack-set',
        'remove-instances',
        '--stack-set', STACK,
        '--accounts', '123456789', '987654321',
        '--regions', 'eu-central-1', 'eu-west-1',
        '--retain',
        '--region-order', 'eu-central-1', 'eu-west-1',
        '--max-concurrent-percentage', '1',
        '--failure-tolerance-percentage', '1',
    ])

    client.delete_stack_instances.assert_called_with(
        StackSetName=STACK,
        Accounts=['123456789', '987654321'],
        Regions=['eu-central-1', 'eu-west-1'],
        RetainStacks=True,
        OperationPreferences={
            'RegionOrder': ['eu-central-1', 'eu-west-1'],
            'FailureTolerancePercentage': 1,
            'MaxConcurrentPercentage': 1
        }
    )


def test_remove_all_stack_set_instances(client, loader):
    client.list_accounts.return_value = ACCOUNTS
    client.get_caller_identity.return_value = {'Account': '5678'}
    client.describe_regions.return_value = EC2_REGIONS
    cli.main([
        'stack-set',
        'remove-instances',
        '--stack-set', STACK,
        '--all-accounts',
        '--all-regions',
    ])

    client.delete_stack_instances.assert_called_with(
        StackSetName=STACK,
        Accounts=['1234', '5678'],
        Regions=['us-west-1', 'us-west-2'],
        RetainStacks=False
    )


def test_remove_stack_set(client, loader):
    cli.main([
        'stack-set',
        'remove',
        '--stack-set', STACK,
    ])

    client.delete_stack_set.assert_called_with(
        StackSetName=STACK
    )


def test_excluded_regions_with_preference(client, logger, loader):
    client.update_stack_set.return_value = {'OperationId': '12345'}
    client.get_caller_identity.return_value = {'Account': '5678'}
    client.list_accounts.return_value = ACCOUNTS
    client.describe_regions.return_value = EC2_REGIONS
    cli.main([
        'stack-set',
        'update',
        '--stack-set', STACK,
        '--all-accounts',
        '--excluded-regions',
        'us-west-1',
        '--all-regions'
    ])

    client.update_stack_set.assert_called_with(
        StackSetName=STACK,
        TemplateBody=TEMPLATE,
        Accounts=['1234', '5678'],
        Regions=['us-west-2']
    )


def test_main_account_only_deployment_with_preference(client, logger, loader):
    client.update_stack_set.return_value = {'OperationId': '12345'}
    client.list_accounts.return_value = ACCOUNTS
    client.describe_regions.return_value = EC2_REGIONS
    accountid = str(uuid4())
    client.get_caller_identity.return_value = {'Account': accountid}
    cli.main([
        'stack-set',
        'update',
        '--stack-set', STACK,
        '--main-account',
        '--all-accounts',
        '--excluded-regions',
        'us-west-1'
    ])

    client.update_stack_set.assert_called_with(
        StackSetName=STACK,
        TemplateBody=TEMPLATE,
        Accounts=[accountid],
        Regions=['us-west-2']
    )


def test_diff_cli_call(template, mocker, client, session):
    diff = mocker.patch('formica.diff.compare_stack_set')
    cli.main(['stack-set', 'diff', '--stack-set', STACK, '--main-account-parameter'])
    diff.assert_called_with(stack=STACK, parameters={}, vars={}, tags={}, main_account_parameter=True)


def test_diff_cli_call_with_vars(template, mocker, client, session):
    diff = mocker.patch('formica.diff.compare_stack_set')
    cli.main(['stack-set', 'diff', '--stack', STACK, '--vars', 'V=1', '--parameters', 'P=2', '--tags', 'T=3'])
    diff.assert_called_with(stack=STACK, vars={'V': '1'}, parameters={'P': '2'}, tags={'T': '3'},
                            main_account_parameter=False)
