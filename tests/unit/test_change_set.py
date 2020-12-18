import pytest
from mock import Mock
import json
import copy

from botocore.exceptions import WaiterError, ClientError

from formica.change_set import ChangeSet, CHANGE_SET_HEADER
from tests.unit.constants import (
    STACK, TEMPLATE, CHANGE_SET_TYPE, CHANGESETNAME, CHANGESETCHANGES,
    CHANGE_SET_PARAMETERS, ROLE_ARN, CHANGE_SET_STACK_TAGS,
    CHANGESETCHANGES_WITH_DUPLICATE_CHANGED_PARAMETER, REGION, UUID, RESOURCES, CHANGE_SET_ID, CHANGESET_NESTED_CHANGES
)


@pytest.fixture
def time(mocker):
    return mocker.patch('formica.change_set.time')


@pytest.fixture
def change_set_not_found():
    return ClientError(dict(Error=dict(Code='ChangeSetNotFound')), "DescribeChangeSet")


@pytest.fixture
def logger(mocker):
    return mocker.patch('formica.change_set.logger')


@pytest.fixture
def client(mocker):
    s3_boto = mocker.patch('formica.s3.boto3')
    boto = mocker.patch('formica.change_set.boto3')
    client = mocker.patch('formica.change_set.cf')
    return client


@pytest.fixture
def temp_bucket_function(mocker):
    return mocker.patch('formica.change_set.temporary_bucket')


@pytest.fixture
def temp_bucket(mocker, temp_bucket_function):
    tempbucket_mock = mocker.Mock()
    temp_bucket_function.return_value.__enter__.return_value = tempbucket_mock
    return tempbucket_mock


# @pytest.fixture
# def uuid(mocker):
#     uuid = mocker.patch('formica.change_set.uuid')
#     uuid.uuid4.return_value = UUID
#     return uuid


def test_submits_changeset_and_waits(client):
    change_set = ChangeSet(STACK)

    change_set.create(template=TEMPLATE, change_set_type=CHANGE_SET_TYPE)

    client.create_change_set.assert_called_with(
        StackName=STACK, TemplateBody=TEMPLATE,
        ChangeSetName=CHANGESETNAME, ChangeSetType=CHANGE_SET_TYPE, IncludeNestedStacks=True)

    client.get_waiter.assert_called_with(
        'change_set_create_complete')
    client.get_waiter.return_value.wait.assert_called_with(
        StackName=STACK, ChangeSetName=CHANGESETNAME, WaiterConfig={'Delay': 10, 'MaxAttempts': 120})


def test_creates_and_removes_bucket_for_s3_flag(client, temp_bucket_function, temp_bucket):
    change_set = ChangeSet(STACK)
    bucket_name = 'formica-deploy-{}'.format("test")
    bucket_path = '{}-template.json'.format(STACK)
    template_url = 'https://{}.s3.amazonaws.com/{}'.format(bucket_name, bucket_path)
    temp_bucket.add.return_value = bucket_path
    temp_bucket.name = bucket_name

    change_set.create(template=TEMPLATE, change_set_type=CHANGE_SET_TYPE, s3=True)

    temp_bucket.add.assert_called_with(TEMPLATE)
    temp_bucket_function.assert_called_with(STACK)

    client.create_change_set.assert_called_with(
        StackName=STACK, TemplateURL=template_url,
        ChangeSetName=CHANGESETNAME, ChangeSetType=CHANGE_SET_TYPE, IncludeNestedStacks=True)


def test_submits_changeset_with_parameters(client):
    change_set = ChangeSet(STACK)

    change_set.create(template=TEMPLATE, change_set_type=CHANGE_SET_TYPE, parameters=CHANGE_SET_PARAMETERS)

    Parameters = [
        {'ParameterKey': 'A', 'ParameterValue': 'B', 'UsePreviousValue': False},
        {'ParameterKey': 'B', 'ParameterValue': '2', 'UsePreviousValue': False},
        {'ParameterKey': 'C', 'ParameterValue': 'True', 'UsePreviousValue': False},
    ]
    client.create_change_set.assert_called_with(
        StackName=STACK, TemplateBody=TEMPLATE,
        ChangeSetName=CHANGESETNAME, ChangeSetType=CHANGE_SET_TYPE, Parameters=Parameters, IncludeNestedStacks=True)

    client.get_waiter.assert_called_with(
        'change_set_create_complete')
    client.get_waiter.return_value.wait.assert_called_with(
        StackName=STACK, ChangeSetName=CHANGESETNAME, WaiterConfig={'Delay': 10, 'MaxAttempts': 120})


def test_submits_changeset_with_stack_tags(client):
    change_set = ChangeSet(STACK)

    change_set.create(template=TEMPLATE, change_set_type=CHANGE_SET_TYPE, tags=CHANGE_SET_STACK_TAGS)

    Tags = [
        {'Key': 'T1', 'Value': 'TV1'},
        {'Key': 'T2', 'Value': 'TV2'}
    ]
    client.create_change_set.assert_called_with(
        StackName=STACK, TemplateBody=TEMPLATE,
        ChangeSetName=CHANGESETNAME, ChangeSetType=CHANGE_SET_TYPE, Tags=Tags, IncludeNestedStacks=True)

    client.get_waiter.assert_called_with(
        'change_set_create_complete')
    client.get_waiter.return_value.wait.assert_called_with(
        StackName=STACK, ChangeSetName=CHANGESETNAME, WaiterConfig={'Delay': 10, 'MaxAttempts': 120})


def test_submits_changeset_with_role_arn(client):
    change_set = ChangeSet(STACK)

    change_set.create(template=TEMPLATE, change_set_type=CHANGE_SET_TYPE, role_arn=ROLE_ARN)

    client.create_change_set.assert_called_with(
        StackName=STACK, TemplateBody=TEMPLATE,
        ChangeSetName=CHANGESETNAME, ChangeSetType=CHANGE_SET_TYPE, RoleARN=ROLE_ARN, IncludeNestedStacks=True)

    client.get_waiter.assert_called_with(
        'change_set_create_complete')
    client.get_waiter.return_value.wait.assert_called_with(
        StackName=STACK, ChangeSetName=CHANGESETNAME, WaiterConfig={'Delay': 10, 'MaxAttempts': 120})


def test_submits_changeset_with_capabilities(client):
    change_set = ChangeSet(STACK)

    change_set.create(template=TEMPLATE, change_set_type=CHANGE_SET_TYPE, parameters={},
                      tags={}, capabilities=['A', 'B'])

    client.create_change_set.assert_called_with(
        StackName=STACK, TemplateBody=TEMPLATE,
        ChangeSetName=CHANGESETNAME, ChangeSetType=CHANGE_SET_TYPE, Capabilities=['A', 'B'], IncludeNestedStacks=True)

    client.get_waiter.assert_called_with(
        'change_set_create_complete')
    client.get_waiter.return_value.wait.assert_called_with(
        StackName=STACK, ChangeSetName=CHANGESETNAME, WaiterConfig={'Delay': 10, 'MaxAttempts': 120})


def test_prints_error_message_for_failed_submit_and_exits(capsys, logger, client):
    change_set = ChangeSet(STACK)

    error = WaiterError('name', 'reason', {'StatusReason': 'StatusReason'})
    client.get_waiter.return_value.wait.side_effect = error

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        change_set.create(template=TEMPLATE, change_set_type=CHANGE_SET_TYPE)
    logger.info.assert_called_with('StatusReason')
    assert pytest_wrapped_e.value.code == 1


def test_prints_error_message_and_does_not_fail_without_StatusReason(capsys, logger, client):
    change_set = ChangeSet(STACK)

    error = WaiterError('name', 'reason', {})
    client.get_waiter.return_value.wait.side_effect = error

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        change_set.create(template=TEMPLATE, change_set_type=CHANGE_SET_TYPE)
    logger.info.assert_called()
    assert pytest_wrapped_e.value.code == 1


def test_prints_error_message_but_exits_successfully_for_no_changes(capsys, logger, mocker, client):
    change_set = ChangeSet(STACK)
    status_reason = "The submitted information didn't contain changes. " \
                    "Submit different information to create a change set."

    error = WaiterError('name', 'reason', {'StatusReason': status_reason})
    client.get_waiter.return_value.wait.side_effect = error

    change_set.create(template=TEMPLATE, change_set_type=CHANGE_SET_TYPE)
    logger.info.assert_called_with(status_reason)


def test_remove_existing_changeset_for_update_type(mocker, capsys, client, change_set_not_found, time):
    mocker.patch.object(ChangeSet, 'describe')
    change_set = ChangeSet(STACK)
    client.describe_change_set.side_effect = [
        {"ChangeSetId": CHANGESETNAME}, {}, change_set_not_found]
    change_set.create(template=TEMPLATE, change_set_type='UPDATE')
    client.describe_change_set.assert_called_with(StackName=STACK, ChangeSetName=CHANGESETNAME)
    client.delete_change_set.assert_called_with(ChangeSetName=CHANGESETNAME)
    time.sleep.assert_called_with(5)


def test_do_not_remove_changeset_if_non_existent(client, change_set_not_found):
    change_set = ChangeSet(STACK)
    client.describe_change_set.side_effect = change_set_not_found
    change_set.remove_existing_changeset()
    client.delete_change_set.assert_not_called()


def test_exception_if_change_set_not_deleted(client, time):
    change_set = ChangeSet(STACK)
    with pytest.raises(Exception) as pytest_exception:
        change_set.remove_existing_changeset()


def test_reraises_exception_when_not_change_set_not_found(client):
    change_set = ChangeSet(STACK)
    exception = ClientError(dict(Error=dict(
        Code='ValidationError')), "DescribeChangeSet")
    client.describe_change_set.side_effect = exception
    with pytest.raises(ClientError):
        change_set.remove_existing_changeset()


def test_prints_changes(logger, client):
    client.describe_change_set.return_value = CHANGESETCHANGES
    change_set = ChangeSet(STACK)

    change_set.describe()

    change_set_output = '\n'.join([call[1][0] for call in logger.info.mock_calls])

    to_search = []
    to_search.extend(CHANGE_SET_HEADER)
    to_search.extend(['Remove', 'Modify', 'Add'])
    to_search.extend(['DeploymentBucket', 'DeploymentBucket2', 'DeploymentBucket3'])
    to_search.extend(['simpleteststack-deploymentbucket-1l7p61v6fxpry ',
                      'simpleteststack-deploymentbucket2-11ngaeftydtn7 '])
    to_search.extend(['AWS::S3::Bucket'])
    to_search.extend(['True'])
    to_search.extend(['BucketName, Tags'])
    # Parameters
    to_search.extend(['bucketname=formicatestbucketname, bucketname2=formicatestbucketname2'])
    # Capabilities
    to_search.extend(['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM'])
    # Stack Tags
    to_search.extend(['StackKey=StackValue, StackKey2=StackValue2'])
    for term in to_search:
        assert term in change_set_output

    assert 'None' not in change_set_output


def test_prints_nested_changes(logger, client):
    client.describe_change_set.side_effect = [CHANGESET_NESTED_CHANGES, CHANGESETCHANGES]
    change_set = ChangeSet(STACK)

    change_set.describe()

    change_set_output = '\n'.join([call[1][0] for call in logger.info.mock_calls])
    print(change_set_output)

    to_search = []
    to_search.extend(CHANGE_SET_HEADER)
    to_search.extend(['Changes for nested Stack: NestedStack'])
    to_search.extend(['NestedStack'])
    to_search.extend(['Remove', 'Modify', 'Add'])
    to_search.extend(['DeploymentBucket', 'DeploymentBucket2', 'DeploymentBucket3'])
    to_search.extend(['simpleteststack-deploymentbucket-1l7p61v6fxpry ',
                      'simpleteststack-deploymentbucket2-11ngaeftydtn7 '])
    to_search.extend(['AWS::S3::Bucket'])
    to_search.extend(['True'])
    to_search.extend(['BucketName, Tags'])
    for term in to_search:
        assert term in change_set_output

    assert 'None' not in change_set_output


def test_only_prints_unique_changed_parameters(logger, client):
    client.describe_change_set.return_value = CHANGESETCHANGES_WITH_DUPLICATE_CHANGED_PARAMETER
    change_set = ChangeSet(STACK)

    change_set.describe()

    change_set_output = logger.info.call_args[0][0]

    assert change_set_output.count('BucketName') == 1


def test_change_set_with_resource_types(client):
    resources = {
        'Resources': {resource: {'Type': resource} for resource in RESOURCES}
    }
    template = json.dumps(resources)
    change_set = ChangeSet(STACK)

    change_set.create(template=template, change_set_type=CHANGE_SET_TYPE, resource_types=True)

    client.create_change_set.assert_called_with(
        StackName=STACK, TemplateBody=template,
        ChangeSetName=CHANGESETNAME, ChangeSetType=CHANGE_SET_TYPE, ResourceTypes=list(set(RESOURCES)),
        IncludeNestedStacks=True)


def test_change_set_with_previous_template(client):
    change_set = ChangeSet(STACK)

    change_set.create(change_set_type=CHANGE_SET_TYPE, use_previous_template=True)

    client.create_change_set.assert_called_with(
        StackName=STACK,
        ChangeSetName=CHANGESETNAME, ChangeSetType=CHANGE_SET_TYPE, UsePreviousTemplate=True, IncludeNestedStacks=True)


def test_change_set_with_previous_parameters(client):
    Parameters = [
        {'ParameterKey': 'A', 'UsePreviousValue': True},
        {'ParameterKey': 'B', 'UsePreviousValue': True},
        {'ParameterKey': 'C', 'ParameterValue': '12345', 'UsePreviousValue': False},
        {'ParameterKey': 'D', 'ParameterValue': '7890', 'UsePreviousValue': False},
    ]

    client.describe_stacks.return_value = {
        'Stacks': [{'Parameters': [{'ParameterKey': 'A'}, {'ParameterKey': 'B'}]}]
    }
    change_set = ChangeSet(STACK)

    change_set.create(change_set_type=CHANGE_SET_TYPE, use_previous_template=True, use_previous_parameters=True,
                      parameters={'C': '12345', 'D': '7890'})
    client.describe_stacks.assert_called_once_with(StackName=STACK)

    client.create_change_set.assert_called_with(
        StackName=STACK,
        ChangeSetName=CHANGESETNAME, ChangeSetType=CHANGE_SET_TYPE, Parameters=Parameters, UsePreviousTemplate=True,
        IncludeNestedStacks=True)


def test_change_set_without_named_properties(client):
    CHANGESET = copy.deepcopy(CHANGESETCHANGES)

    # Find a property change in the changeset
    PROPERTY_CHANGE = CHANGESET['Changes'][1]['ResourceChange']['Details'][1]
    assert PROPERTY_CHANGE['Target']['Attribute'] == 'Properties'
    assert PROPERTY_CHANGE['Target']['Name'] == 'BucketName'

    # Remove the "Name" attribute
    del PROPERTY_CHANGE['Target']['Name']

    client.describe_change_set.return_value = CHANGESET

    change_set = ChangeSet(STACK)
    change_set.describe()
