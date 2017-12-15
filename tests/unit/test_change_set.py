import pytest
from mock import Mock

from botocore.exceptions import WaiterError, ClientError

from formica.change_set import ChangeSet, CHANGE_SET_HEADER
from tests.unit.constants import (
    STACK, TEMPLATE, CHANGE_SET_TYPE, CHANGESETNAME, CHANGESETCHANGES,
    CHANGE_SET_PARAMETERS, ROLE_ARN, CHANGE_SET_STACK_TAGS,
    CHANGESETCHANGES_WITH_DUPLICATE_CHANGED_PARAMETER,
)


@pytest.fixture
def logger(mocker):
    return mocker.patch('formica.change_set.logger')


def test_submits_changeset_and_waits():
    cf_client_mock = Mock()
    change_set = ChangeSet(STACK, cf_client_mock)

    change_set.create(template=TEMPLATE, change_set_type=CHANGE_SET_TYPE)

    cf_client_mock.create_change_set.assert_called_with(
        StackName=STACK, TemplateBody=TEMPLATE,
        ChangeSetName=CHANGESETNAME, ChangeSetType=CHANGE_SET_TYPE)

    cf_client_mock.get_waiter.assert_called_with(
        'change_set_create_complete')
    cf_client_mock.get_waiter.return_value.wait.assert_called_with(
        StackName=STACK, ChangeSetName=CHANGESETNAME)


def test_submits_changeset_with_parameters():
    cf_client_mock = Mock()
    change_set = ChangeSet(STACK, cf_client_mock)

    change_set.create(template=TEMPLATE, change_set_type=CHANGE_SET_TYPE, parameters=CHANGE_SET_PARAMETERS)

    Parameters = [
        {'ParameterKey': 'A', 'ParameterValue': 'B', 'UsePreviousValue': False},
        {'ParameterKey': 'B', 'ParameterValue': 'C', 'UsePreviousValue': False}
    ]
    cf_client_mock.create_change_set.assert_called_with(
        StackName=STACK, TemplateBody=TEMPLATE,
        ChangeSetName=CHANGESETNAME, ChangeSetType=CHANGE_SET_TYPE, Parameters=Parameters)

    cf_client_mock.get_waiter.assert_called_with(
        'change_set_create_complete')
    cf_client_mock.get_waiter.return_value.wait.assert_called_with(
        StackName=STACK, ChangeSetName=CHANGESETNAME)


def test_submits_changeset_with_stack_tags():
    cf_client_mock = Mock()
    change_set = ChangeSet(STACK, cf_client_mock)

    change_set.create(template=TEMPLATE, change_set_type=CHANGE_SET_TYPE, tags=CHANGE_SET_STACK_TAGS)

    Tags = [
        {'Key': 'A', 'Value': 'B'},
        {'Key': 'B', 'Value': 'C'}
    ]
    cf_client_mock.create_change_set.assert_called_with(
        StackName=STACK, TemplateBody=TEMPLATE,
        ChangeSetName=CHANGESETNAME, ChangeSetType=CHANGE_SET_TYPE, Tags=Tags)

    cf_client_mock.get_waiter.assert_called_with(
        'change_set_create_complete')
    cf_client_mock.get_waiter.return_value.wait.assert_called_with(
        StackName=STACK, ChangeSetName=CHANGESETNAME)


def test_submits_changeset_with_role_arn():
    cf_client_mock = Mock()
    change_set = ChangeSet(STACK, cf_client_mock)

    change_set.create(template=TEMPLATE, change_set_type=CHANGE_SET_TYPE, role_arn=ROLE_ARN)

    cf_client_mock.create_change_set.assert_called_with(
        StackName=STACK, TemplateBody=TEMPLATE,
        ChangeSetName=CHANGESETNAME, ChangeSetType=CHANGE_SET_TYPE, RoleArn=ROLE_ARN)

    cf_client_mock.get_waiter.assert_called_with(
        'change_set_create_complete')
    cf_client_mock.get_waiter.return_value.wait.assert_called_with(
        StackName=STACK, ChangeSetName=CHANGESETNAME)


def test_submits_changeset_with_capabilities():
    cf_client_mock = Mock()
    change_set = ChangeSet(STACK, cf_client_mock)

    change_set.create(template=TEMPLATE, change_set_type=CHANGE_SET_TYPE, parameters={},
                      tags={}, capabilities=['A', 'B'])

    cf_client_mock.create_change_set.assert_called_with(
        StackName=STACK, TemplateBody=TEMPLATE,
        ChangeSetName=CHANGESETNAME, ChangeSetType=CHANGE_SET_TYPE, Capabilities=['A', 'B'])

    cf_client_mock.get_waiter.assert_called_with(
        'change_set_create_complete')
    cf_client_mock.get_waiter.return_value.wait.assert_called_with(
        StackName=STACK, ChangeSetName=CHANGESETNAME)


def test_prints_error_message_for_failed_submit_and_exits(capsys, logger):
    cf_client_mock = Mock()
    change_set = ChangeSet(STACK, cf_client_mock)

    error = WaiterError('name', 'reason', {'StatusReason': 'StatusReason'})
    cf_client_mock.get_waiter.return_value.wait.side_effect = error

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        change_set.create(template=TEMPLATE, change_set_type=CHANGE_SET_TYPE)
    logger.info.assert_called_with('StatusReason')
    assert pytest_wrapped_e.value.code == 1


def test_prints_error_message_and_does_not_fail_without_StatusReason(capsys, logger):
    cf_client_mock = Mock()
    change_set = ChangeSet(STACK, cf_client_mock)

    error = WaiterError('name', 'reason', {})
    cf_client_mock.get_waiter.return_value.wait.side_effect = error

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        change_set.create(template=TEMPLATE, change_set_type=CHANGE_SET_TYPE)
    logger.info.assert_called()
    assert pytest_wrapped_e.value.code == 1


def test_prints_error_message_but_exits_successfully_for_no_changes(capsys, logger, mocker):
    cf_client_mock = Mock()
    change_set = ChangeSet(STACK, cf_client_mock)
    status_reason = "The submitted information didn't contain changes. " \
                    "Submit different information to create a change set."

    error = WaiterError('name', 'reason', {'StatusReason': status_reason})
    cf_client_mock.get_waiter.return_value.wait.side_effect = error

    change_set.create(template=TEMPLATE, change_set_type=CHANGE_SET_TYPE)
    logger.info.assert_called_with(status_reason)


def test_remove_existing_changeset_for_update_type(mocker, capsys):
    mocker.patch.object(ChangeSet, 'describe')
    cf_client_mock = Mock()
    change_set = ChangeSet(STACK, cf_client_mock)
    change_set.create(template=TEMPLATE, change_set_type='UPDATE')
    cf_client_mock.describe_change_set.assert_called_with(StackName=STACK, ChangeSetName=CHANGESETNAME)
    cf_client_mock.delete_change_set.assert_called_with(StackName=STACK, ChangeSetName=CHANGESETNAME)


def test_do_not_remove_changeset_if_non_existent():
    cf_client_mock = Mock()
    change_set = ChangeSet(STACK, cf_client_mock)
    exception = ClientError(dict(Error=dict(Code='ChangeSetNotFound')), "DescribeChangeSet")
    cf_client_mock.describe_change_set.side_effect = exception
    change_set.remove_existing_changeset()
    cf_client_mock.delete_change_set.assert_not_called()


def test_reraises_exception_when_not_change_set_not_found():
    cf_client_mock = Mock()
    change_set = ChangeSet(STACK, cf_client_mock)
    exception = ClientError(dict(Error=dict(
        Code='ValidationError')), "DescribeChangeSet")
    cf_client_mock.describe_change_set.side_effect = exception
    with pytest.raises(ClientError):
        change_set.remove_existing_changeset()


def test_prints_changes(logger):
    cf_client_mock = Mock()
    cf_client_mock.describe_change_set.return_value = CHANGESETCHANGES
    change_set = ChangeSet(STACK, cf_client_mock)

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


def test_only_prints_unique_changed_parameters(logger):
    cf_client_mock = Mock()
    cf_client_mock.describe_change_set.return_value = CHANGESETCHANGES_WITH_DUPLICATE_CHANGED_PARAMETER
    change_set = ChangeSet(STACK, cf_client_mock)

    change_set.describe()

    change_set_output = logger.info.call_args[0][0]

    assert change_set_output.count('BucketName') == 1
