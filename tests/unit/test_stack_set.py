import pytest
import json
from botocore.exceptions import ClientError

from uuid import uuid4

from formica import cli, stack_set
from tests.unit.constants import STACK, CLOUDFORMATION_PARAMETERS, CLOUDFORMATION_TAGS
from tests.unit.constants import TEMPLATE, EC2_REGIONS, ACCOUNTS, ACCOUNT_ID, OPERATION_ID

from path import Path


@pytest.fixture
def logger(mocker):
    return mocker.patch('formica.stack_set.logger')


@pytest.fixture
def client(aws_client, paginators):
    aws_client.create_stack_instances.return_value = {'OperationId': OPERATION_ID}
    aws_client.delete_stack_instances.return_value = {'OperationId': OPERATION_ID}
    aws_client.update_stack_set.return_value = {'OperationId': OPERATION_ID}
    aws_client.get_paginator.side_effect = paginators(list_stack_instances=[], list_accounts=[ACCOUNTS])
    exception = ClientError(
        dict(Error={'Code': 'StackSetNotFoundException'}), "DescribeStackSet")
    aws_client.describe_stack_set.side_effect = exception
    return aws_client


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


@pytest.fixture
def compare(mocker):
    return mocker.patch('formica.stack_set.compare_stack_set')


@pytest.fixture
def input(mocker):
    input_mock = mocker.patch('formica.stack_set.input')
    input_mock.return_value = 'yes'
    return input_mock


@pytest.fixture
def time(mocker):
    return mocker.patch('formica.stack_set.time')


@pytest.fixture
def wait(mocker):
    return mocker.patch('formica.stack_set.wait_for_stack_set_operation')


def dump_template(template):
    return json.dumps(template, indent=None, sort_keys=True, separators=(',', ':'))


def test_create_stack_set(client, logger, loader):
    cli.main([
        'stack-set',
        'create',
        '--stack-set', STACK,
        '--parameters', 'P1=PV1', 'P2=PV2',
        '--tags', 'T1=TV1', 'T2=TV2',
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


def test_create_stack_set_with_main_account(boto_client, client, logger, tmpdir):
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

    boto_client.assert_called_with('sts')

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


def test_do_not_create_if_existing(session, logger, tmpdir, mocker):
    client = mocker.Mock()
    session.return_value.client.return_value = client
    accountid = str(uuid4())
    client.get_caller_identity.return_value = {'Account': accountid}
    client.describe_stack_set().return_value = {}
    with Path(tmpdir):
        with open('test.template.json', 'w') as f:
            f.write(json.dumps({'Parameters': {'SomeParam': {'Type': 'String'}}}))
        cli.main([
            'stack-set',
            'create',
            '--stack-set', STACK,
        ])

    client.create_stack_set.assert_not_called()


def test_update_stack_set_with_compare_check(client, loader, input, compare, wait):
    client.describe_stack_set_operation.return_value = {'StackSetOperation': {'Status': 'SUCCEEDED'}}

    cli.main([
        'stack-set',
        'update',
        '--stack-set', STACK,
        '--parameters', 'P1=PV1', 'P2=PV2',
        '--tags', 'T1=TV1', 'T2=TV2',
        '--vars', 'V1=VV1',
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

    input.assert_called_once()
    wait.assert_called_with(STACK, OPERATION_ID)


def test_update_stack_set_yes_ignores_input(client, loader, input, compare, wait):
    client.describe_stack_set_operation.return_value = {'StackSetOperation': {'Status': 'SUCCEEDED'}}

    cli.main([
        'stack-set',
        'update',
        '--stack-set', STACK,
        '--yes'
    ])

    client.update_stack_set.assert_called_with(
        StackSetName=STACK,
        TemplateBody=TEMPLATE
    )

    input.assert_not_called()


def test_update_stack_set_with_main_account(boto_client, client, logger, tmpdir, input, compare, wait):
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

    boto_client.assert_any_call('sts')
    boto_client.assert_any_call('cloudformation')

    client.update_stack_set.assert_called_with(
        StackSetName=STACK,
        TemplateBody=dump_template({'Parameters': {'MainAccount': {'Type': 'String', 'Default': accountid}}})
    )


def test_update_stack_set_with_all_regions_and_accounts(client, logger, loader, input, compare, wait):
    client.get_caller_identity.return_value = {'Account': '5678'}
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


def test_update_stack_set_with_all_subaccounts(client, logger, loader, input, compare, wait):
    client.update_stack_set.return_value = {'OperationId': '12345'}
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


def test_update_stack_set_with_excluded_accounts(client, logger, loader, input, compare, wait):
    client.update_stack_set.return_value = {'OperationId': '12345'}
    client.get_caller_identity.return_value = {'Account': '5678'}
    client.describe_regions.return_value = EC2_REGIONS
    cli.main([
        'stack-set',
        'add-instances',
        '--stack-set', STACK,
        '--excluded-accounts', '1234',
        '--regions', 'eu-central-1'
    ])

    client.create_stack_instances.assert_called_with(
        StackSetName=STACK,
        Accounts=['5678'],
        Regions=['eu-central-1']
    )


def test_update_with_create_missing(client, logger, loader, input, compare, wait):
    client.update_stack_set.return_value = {'OperationId': '12345'}
    client.get_caller_identity.return_value = {'Account': '5678'}
    client.describe_regions.return_value = EC2_REGIONS
    cli.main([
        'stack-set',
        'update',
        '--stack-set', STACK,
        '--all-subaccounts',
        '--create-missing'
    ])

    client.create_stack_set.assert_called_with(
        StackSetName=STACK,
        TemplateBody=TEMPLATE
    )

    client.describe_stack_set.assert_called_with(StackSetName=STACK)


def test_add_stack_set_instances(client, loader, wait, input):
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

    wait.assert_called_with(STACK, OPERATION_ID)


def test_stack_set_accounts_converts_to_string():
    assert stack_set.accounts({'accounts': ['123', 12345, 54321]}) == ['123', '12345', '54321']


def test_add_all_stack_set_instances(client, loader, wait, input):
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


def test_add_stack_set_instances_with_operation_preferences(client, loader, wait, input):
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


def test_add_only_missing_stack_set_instances(client, loader, wait, input, mocker, paginators):
    client.get_paginator.side_effect = paginators(list_stack_instances=[
        {'Summaries': [{'Account': '123456789', "Region": 'eu-central-1'}]}])
    cli.main([
        'stack-set',
        'add-instances',
        '--accounts', '123456789', '987654321',
        '--regions', 'eu-central-1', 'eu-west-1',
        '--stack-set', STACK
    ])

    assert client.create_stack_instances.mock_calls == [
        mocker.call(
            StackSetName=STACK,
            Accounts=['987654321'],
            Regions=['eu-central-1']
        ),
        mocker.call(
            StackSetName=STACK,
            Accounts=['123456789', '987654321'],
            Regions=['eu-west-1']
        )
    ]


def test_add_only_missing_stack_set_instances_with_one_call_if_possible(client, loader, wait, input, mocker,
                                                                        paginators):
    client.get_paginator.side_effect = paginators(list_stack_instances=[
        {'Summaries': [{'Account': '123456789', "Region": 'eu-central-1'},
                       {'Account': '987654321', "Region": 'eu-central-1'}]}])
    cli.main([
        'stack-set',
        'add-instances',
        '--accounts', '123456789', '987654321',
        '--regions', 'eu-central-1', 'eu-west-1',
        '--stack-set', STACK
    ])

    assert client.create_stack_instances.mock_calls == [
        mocker.call(
            StackSetName=STACK,
            Accounts=['123456789', '987654321'],
            Regions=['eu-west-1']
        )
    ]

    client.get_paginator.side_effect = paginators(list_stack_instances=[
        {'Summaries': [{'Account': '123456789', "Region": 'eu-central-1'},
                       {'Account': '123456789', "Region": 'eu-west-1'}]}])

    cli.main([
        'stack-set',
        'add-instances',
        '--accounts', '123456789', '987654321',
        '--regions', 'eu-central-1', 'eu-west-1',
        '--stack-set', STACK
    ])

    assert len(client.create_stack_instances.mock_calls) == 2

    client.create_stack_instances.assert_called_with(
        StackSetName=STACK,
        Accounts=['987654321'],
        Regions=['eu-central-1', 'eu-west-1']
    )


def test_remove_stack_set_instances(client, loader, wait, input):
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

    wait.assert_called_with(STACK, OPERATION_ID)


def test_remove_all_stack_set_instances(client, loader, wait, input):
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


def test_excluded_regions_with_preference(client, logger, loader, input, compare, wait):
    client.update_stack_set.return_value = {'OperationId': '12345'}
    client.get_caller_identity.return_value = {'Account': '5678'}
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


def test_main_account_only_deployment_with_preference(client, logger, loader, compare, input, wait):
    client.update_stack_set.return_value = {'OperationId': '12345'}
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


def test_stack_set_waiter(client, loader, compare, time):
    client.describe_stack_set_operation.side_effect = [{'StackSetOperation': {'Status': state}} for state in
                                                       ['RUNNING', 'SUCCEEDED']]

    cli.main([
        'stack-set',
        'update',
        '--stack-set', STACK,
        '--yes'
    ])

    client.update_stack_set.assert_called_with(
        StackSetName=STACK,
        TemplateBody=TEMPLATE
    )

    time.sleep.assert_called_with(5)
    assert time.sleep.call_count == 2


def test_stack_set_waiter_exits_on_failed_operation(client, loader, input, compare, time):
    client.describe_stack_set_operation.side_effect = [{'StackSetOperation': {'Status': state}} for state in
                                                       ['RUNNING', 'FAILED']]

    with pytest.raises(SystemExit, match='1'):
        cli.main([
            'stack-set',
            'update',
            '--stack-set', STACK,
            '--yes'
        ])

    client.update_stack_set.assert_called_with(
        StackSetName=STACK,
        TemplateBody=TEMPLATE
    )

    time.sleep.assert_called_with(5)
    assert time.sleep.call_count == 2
