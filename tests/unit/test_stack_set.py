import pytest
from uuid import uuid4

from formica import cli
from tests.unit.constants import STACK, CLOUDFORMATION_PARAMETERS, CLOUDFORMATION_TAGS, TEMPLATE


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


def test_create_stack_set_with_main_account(session, client, logger, mocker):
    mock = mocker.patch('formica.loader.Loader')
    mock.return_value.template.return_value = {}
    accountid = str(uuid4())
    client.get_caller_identity.return_value = {'Account': accountid}
    cli.main([
        'stack-set',
        'create',
        '--stack-set', STACK,
        '--main-account'
    ])

    session.return_value.client.assert_called_with('sts')

    client.create_stack_set.assert_called_with(
        StackSetName=STACK,
        TemplateBody={'Parameters': {'MainAccount': {'Type': 'String'}}},
        Parameters=[{'ParameterKey': 'MainAccount', 'ParameterValue': accountid, 'UsePreviousValue': False}]
    )


def test_create_stack_set_with_main_account_and_existing_parameters(session, client, logger, mocker):
    mock = mocker.patch('formica.loader.Loader')
    mock.return_value.template.return_value = {'Parameters': {'SomeParam': {'Type': 'String'}}}
    accountid = str(uuid4())
    client.get_caller_identity.return_value = {'Account': accountid}
    cli.main([
        'stack-set',
        'create',
        '--stack-set', STACK,
        '--main-account',
        '--parameters', 'A=B'

    ])

    client.create_stack_set.assert_called_with(
        StackSetName=STACK,
        TemplateBody={'Parameters': {'MainAccount': {'Type': 'String'}, 'SomeParam': {'Type': 'String'}}},
        Parameters=[{'ParameterKey': 'A', 'ParameterValue': 'B', 'UsePreviousValue': False}, {
            'ParameterKey': 'MainAccount', 'ParameterValue': accountid, 'UsePreviousValue': False}]
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
        Regions=['eu-central-1', 'eu-west-1']
    )


def test_update_stack_set_with_main_account(session, client, logger, mocker):
    client.update_stack_set.return_value = {'OperationId': '12345'}
    mock = mocker.patch('formica.loader.Loader')
    mock.return_value.template.return_value = {}
    accountid = str(uuid4())
    client.get_caller_identity.return_value = {'Account': accountid}
    cli.main([
        'stack-set',
        'update',
        '--stack-set', STACK,
        '--main-account'
    ])

    session.return_value.client.assert_called_with('sts')

    client.update_stack_set.assert_called_with(
        StackSetName=STACK,
        TemplateBody={'Parameters': {'MainAccount': {'Type': 'String'}}},
        Parameters=[{'ParameterKey': 'MainAccount', 'ParameterValue': accountid, 'UsePreviousValue': False}]
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


def test_remove_stack_set_instances(client, loader):
    cli.main([
        'stack-set',
        'remove-instances',
        '--stack-set', STACK,
        '--accounts', '123456789', '987654321',
        '--regions', 'eu-central-1', 'eu-west-1',
        '--retain'
    ])

    client.delete_stack_instances.assert_called_with(
        StackSetName=STACK,
        Accounts=['123456789', '987654321'],
        Regions=['eu-central-1', 'eu-west-1'],
        RetainStacks=True
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
