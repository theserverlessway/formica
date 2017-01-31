from unittest import TestCase
from unittest.mock import patch, Mock

from botocore.exceptions import NoCredentialsError
from click.testing import CliRunner

from formica import cli
from tests.constants import STACK, PROFILE, REGION, CHANGESETNAME


class TestDeploy(TestCase):
    def run_deploy(self, exit_code=0, exception=None):
        runner = CliRunner()
        result = runner.invoke(cli.deploy, ['--stack', STACK, '--profile', PROFILE, '--region', REGION])
        if result.exit_code != exit_code:
            print(result.output)
            print(result.exception)
            print(result.exit_code)
        self.assertEqual(result.exit_code, exit_code)
        return result

    @patch('formica.helper.AWSSession')
    def test_catches_common_aws_exceptions(self, session):
        session.side_effect = NoCredentialsError()
        self.run_deploy(1)

    def test_fails_if_no_stack_given(self):
        runner = CliRunner()
        result = runner.invoke(cli.deploy)
        self.assertIn('--stack', result.output)
        self.assertEqual(result.exit_code, 2)

    @patch('formica.helper.AWSSession')
    def test_uses_parameters_for_session(self, session):
        self.run_deploy(0)
        session.assert_called_with(REGION, PROFILE)

    @patch('formica.helper.AWSSession')
    def test_gets_cloudformation_client(self, session):
        self.run_deploy(0)
        session.return_value.client_for.assert_called_with('cloudformation')

    @patch('formica.helper.AWSSession')
    def test_executes_change_set_and_waits(self, session):
        cf_client_mock = Mock()
        session.return_value.client_for.return_value = cf_client_mock

        self.run_deploy()
        cf_client_mock.execute_change_set.assert_called_with(ChangeSetName=CHANGESETNAME, StackName=STACK)
        cf_client_mock.get_waiter.assert_called_with('stack_update_complete')
        cf_client_mock.get_waiter.return_value.wait.assert_called_with(StackName=STACK)
