import unittest
from unittest.mock import Mock, patch

from botocore.exceptions import WaiterError, ClientError

from formica.change_set import ChangeSet, CHANGE_SET_HEADER
from tests.constants import STACK, TEMPLATE, CHANGE_SET_TYPE, CHANGESETNAME, CHANGESETCHANGES, CHANGE_SET_PARAMETERS, \
    CHANGESETCHANGES_WITH_DUPLICATE_CHANGED_PARAMETER, CHANGE_SET_STACK_TAGS


class TestChangeSet(unittest.TestCase):
    def test_submits_changeset_and_waits(self):
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

    def test_submits_changeset_with_parameters(self):
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

    def test_submits_changeset_with_stack_tags(self):
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

    def test_submits_changeset_with_capabilities(self):
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

    @patch('formica.change_set.click')
    @patch('formica.change_set.sys')
    def test_prints_error_message_for_failed_submit_and_exits(self, sys, click):
        cf_client_mock = Mock()
        change_set = ChangeSet(STACK, cf_client_mock)

        error = WaiterError('name', 'reason', {'StatusReason': 'StatusReason'})
        cf_client_mock.get_waiter.return_value.wait.side_effect = error

        change_set.create(template=TEMPLATE, change_set_type=CHANGE_SET_TYPE)
        click.echo.assert_called_with('StatusReason')
        sys.exit.assert_called_with(1)

    @patch('formica.change_set.sys')
    @patch.object(ChangeSet, 'describe')
    def test_remove_existing_changeset_for_update_type(self, describe, sys):
        cf_client_mock = Mock()
        change_set = ChangeSet(STACK, cf_client_mock)
        change_set.create(template=TEMPLATE, change_set_type='UPDATE')
        cf_client_mock.describe_change_set.assert_called_with(StackName=STACK, ChangeSetName=CHANGESETNAME)
        cf_client_mock.delete_change_set.assert_called_with(StackName=STACK, ChangeSetName=CHANGESETNAME)

    def test_do_not_remove_changeset_if_non_existent(self):
        cf_client_mock = Mock()
        change_set = ChangeSet(STACK, cf_client_mock)
        exception = ClientError(dict(Error=dict(Code='ChangeSetNotFound')), "DescribeChangeSet")
        cf_client_mock.describe_change_set.side_effect = exception
        change_set.remove_existing_changeset()
        cf_client_mock.delete_change_set.assert_not_called()

    def test_reraises_exception_when_not_change_set_not_found(self):
        cf_client_mock = Mock()
        change_set = ChangeSet(STACK, cf_client_mock)
        exception = ClientError(dict(Error=dict(
            Code='ValidationError')), "DescribeChangeSet")
        cf_client_mock.describe_change_set.side_effect = exception
        with self.assertRaises(ClientError):
            change_set.remove_existing_changeset()

    @patch('formica.change_set.click')
    def test_prints_changes(self, click):
        cf_client_mock = Mock()
        cf_client_mock.describe_change_set.return_value = CHANGESETCHANGES
        change_set = ChangeSet(STACK, cf_client_mock)

        change_set.describe()

        change_set_output = '\n'.join([call[1][0] for call in click.echo.mock_calls])

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
            self.assertIn(term, change_set_output)

        self.assertNotIn('None', change_set_output)

    @patch('formica.change_set.click')
    def test_only_prints_unique_changed_parameters(self, click):
        cf_client_mock = Mock()
        cf_client_mock.describe_change_set.return_value = CHANGESETCHANGES_WITH_DUPLICATE_CHANGED_PARAMETER
        change_set = ChangeSet(STACK, cf_client_mock)

        change_set.describe()

        change_set_output = click.echo.call_args[0][0]

        self.assertEquals(change_set_output.count('BucketName'), 1)
