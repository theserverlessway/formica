from unittest import TestCase
from unittest.mock import patch, Mock

from botocore.exceptions import NoCredentialsError
from click.testing import CliRunner

from formica import cli
from tests.unit.constants import STACK, PROFILE, REGION, CHANGESETNAME, EVENT_ID


class TestDeploy(TestCase):
    def run_deploy(self, exit_code=0, exception=None):
        runner = CliRunner()
        result = runner.invoke(cli.deploy, ['--stack', STACK, '--profile', PROFILE, '--region', REGION])
        self.assertEqual(result.exit_code, exit_code)
        return result

    @patch('formica.cli.StackWaiter')
    @patch('formica.aws.Session')
    def test_catches_common_aws_exceptions(self, session, wait):
        session.side_effect = NoCredentialsError()
        self.run_deploy(1)

    def test_fails_if_no_stack_given(self):
        runner = CliRunner()
        result = runner.invoke(cli.deploy)
        self.assertIn('--stack', result.output)
        self.assertEqual(result.exit_code, 2)

    @patch('formica.cli.StackWaiter')
    @patch('formica.aws.Session')
    def test_gets_cloudformation_client(self, session, wait):
        self.run_deploy(0)
        session.return_value.client.assert_called_with('cloudformation')

    @patch('formica.cli.StackWaiter')
    @patch('formica.aws.Session')
    def test_executes_change_set_and_waits(self, session, stack_waiter):
        cf_client_mock = Mock()
        session.return_value.client.return_value = cf_client_mock
        cf_client_mock.describe_stack_events.return_value = {'StackEvents': [{'EventId': EVENT_ID}]}

        self.run_deploy()
        cf_client_mock.describe_stack_events.assert_called_with(StackName=STACK)
        cf_client_mock.execute_change_set.assert_called_with(ChangeSetName=CHANGESETNAME, StackName=STACK)
        stack_waiter.assert_called_with(STACK, cf_client_mock)
        stack_waiter.return_value.wait.assert_called_with(EVENT_ID)
