import unittest
from unittest.mock import patch, Mock, create_autospec

from botocore.exceptions import WaiterError, ClientError
from click.testing import CliRunner

from formica import cli
from formica.aws_session import AWSSession
from formica.submit import Submit
from tests.test_constants import REGION, PROFILE, STACK, TEMPLATE, CHANGESETNAME


class TestSubmit(unittest.TestCase):
    def run_submit(self, exit_code=0):
        runner = CliRunner()
        result = runner.invoke(cli.submit, ['--stack', STACK, '--profile', PROFILE, '--region', REGION])
        if result.exit_code != exit_code:
            print(result.output)
            print(result.exception)
            print(result.exit_code)
        self.assertEqual(result.exit_code, exit_code)
        return result

    def test_fails_if_no_stack_given(self):
        runner = CliRunner()
        result = runner.invoke(cli.submit)
        self.assertIn('--stack', result.output)
        self.assertEqual(result.exit_code, 2)

    @patch('formica.cli.AWSSession')
    def test_uses_parameters_for_session(self, session):
        self.run_submit(0)
        session.assert_called_with(REGION, PROFILE)

    @patch('formica.cli.AWSSession')
    def test_gets_cloudformation_client(self, session):
        self.run_submit(0)
        session.return_value.client_for.assert_called_with('cloudformation')

    @patch.object(Submit, 'remove_existing_changeset')
    @patch('formica.cli.AWSSession')
    @patch('formica.submit.Loader')
    def test_submits_changeset_and_waits(self, loader, session, remove):
        cf_client_mock = Mock()

        session.return_value.client_for.return_value = cf_client_mock

        loader.return_value.template.return_value = TEMPLATE
        cf_client_mock.describe_change_set.return_value = {'Changes': []}

        self.run_submit(0)
        loader.return_value.load.assert_called_with()

        cf_client_mock.create_change_set.assert_called_with(
            StackName=STACK, TemplateBody=TEMPLATE,
            ChangeSetName=CHANGESETNAME)

        cf_client_mock.get_waiter.assert_called_with(
            'change_set_create_complete')
        cf_client_mock.get_waiter.return_value.wait.assert_called_with(
            StackName=STACK, ChangeSetName=CHANGESETNAME)
        cf_client_mock.describe_change_set.assert_called_with(StackName=STACK, ChangeSetName=CHANGESETNAME)

    @patch('formica.submit.click')
    @patch.object(Submit, 'remove_existing_changeset')
    @patch('formica.cli.AWSSession')
    @patch('formica.submit.Loader')
    def test_prints_error_message_for_failed_submit(self, loader, session, remove, click):
        cf_client_mock = Mock()

        session.return_value.client_for.return_value = cf_client_mock

        loader.return_value.template.return_value = TEMPLATE

        error = WaiterError('name', 'reason', {'StatusReason': 'StatusReason'})
        cf_client_mock.get_waiter.return_value.wait.side_effect = error

        self.run_submit(1)
        loader.return_value.load.assert_called_with()

        click.echo.assert_called_with('StatusReason')

    def test_remove_existing_changeset(self):
        client_mock = Mock()
        session = create_autospec(AWSSession)
        session.client_for.return_value = client_mock
        submit = Submit(STACK, session)
        submit.remove_existing_changeset()
        client_mock.describe_change_set.assert_called_with(StackName=STACK, ChangeSetName=CHANGESETNAME)
        client_mock.delete_change_set.assert_called_with(StackName=STACK, ChangeSetName=CHANGESETNAME)

    def test_no_remove_without_existing_changeset(self):
        client_mock = Mock()
        session = create_autospec(AWSSession)()
        session.client_for.return_value = client_mock
        submit = Submit(STACK, session)
        exception = ClientError(dict(Error=dict(Code='ChangeSetNotFound')), "DescribeChangeSet")
        client_mock.describe_change_set.side_effect = exception
        submit.remove_existing_changeset()
        client_mock.delete_change_set.assert_not_called()

    def test_reraises_exception_when_not_from_change_set(self):
        client_mock = Mock()
        session = create_autospec(AWSSession)()
        session.client_for.return_value = client_mock
        submit = Submit(STACK, session)
        exception = ClientError(dict(Error=dict(
            Code='ValidationError')), "DescribeChangeSet")
        client_mock.describe_change_set.side_effect = exception
        with self.assertRaises(ClientError):
            submit.remove_existing_changeset()
