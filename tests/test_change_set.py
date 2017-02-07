import unittest
from unittest import mock
from unittest.mock import Mock, patch

from botocore.exceptions import WaiterError, ClientError

from formica.change_set import ChangeSet, CHANGE_SET_HEADER
from tests.constants import STACK, TEMPLATE, CHANGE_SET_TYPE, CHANGESETNAME, CHANGESETCHANGES, CHANGE_SET_PARAMETERS


class TestChangeSet(unittest.TestCase):
    def test_submits_changeset_and_waits(self):
        cf_client_mock = Mock()
        change_set = ChangeSet(STACK, cf_client_mock)

        change_set.create(template=TEMPLATE, type=CHANGE_SET_TYPE)

        cf_client_mock.create_change_set.assert_called_with(
            StackName=STACK, TemplateBody=TEMPLATE,
            ChangeSetName=CHANGESETNAME, ChangeSetType=CHANGE_SET_TYPE, Parameters=[])

        cf_client_mock.get_waiter.assert_called_with(
            'change_set_create_complete')
        cf_client_mock.get_waiter.return_value.wait.assert_called_with(
            StackName=STACK, ChangeSetName=CHANGESETNAME)

    def test_submits_changeset_with_parameters(self):
        cf_client_mock = Mock()
        change_set = ChangeSet(STACK, cf_client_mock)

        change_set.create(template=TEMPLATE, type=CHANGE_SET_TYPE, parameters=CHANGE_SET_PARAMETERS)

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

    @patch('formica.change_set.click')
    @patch('formica.change_set.sys')
    def test_prints_error_message_for_failed_submit_and_exits(self, sys, click):
        cf_client_mock = Mock()
        change_set = ChangeSet(STACK, cf_client_mock)

        error = WaiterError('name', 'reason', {'StatusReason': 'StatusReason'})
        cf_client_mock.get_waiter.return_value.wait.side_effect = error

        change_set.create(template=TEMPLATE, type=CHANGE_SET_TYPE)
        click.echo.assert_called_with('StatusReason')
        sys.exit.assert_called_with(1)

    @patch('formica.change_set.sys')
    @patch.object(ChangeSet, 'describe')
    def test_remove_existing_changeset_for_update_type(self, describe, sys):
        cf_client_mock = Mock()
        change_set = ChangeSet(STACK, cf_client_mock)
        change_set.create(template=TEMPLATE, type='UPDATE')
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

        click.echo.assert_called_with(mock.ANY)
        args = click.echo.call_args[0]

        to_search = []
        to_search.extend(CHANGE_SET_HEADER)
        to_search.extend(['Remove', 'Modify', 'Add'])
        to_search.extend(['DeploymentBucket', 'DeploymentBucket2', 'DeploymentBucket3'])
        to_search.extend(['simpleteststack-deploymentbucket-1l7p61v6fxpry ',
                          'simpleteststack-deploymentbucket2-11ngaeftydtn7 '])
        to_search.extend(['AWS::S3::Bucket'])
        to_search.extend(['True'])
        to_search.extend(['Tags, BucketName'])
        change_set_output = args[0]
        for term in to_search:
            self.assertIn(term, change_set_output)
        self.assertNotIn('None', change_set_output)
