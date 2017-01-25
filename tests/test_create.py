import unittest
from unittest.mock import patch, Mock

import botocore
from click.testing import CliRunner

from formica import cli
from tests.test_constants import REGION, PROFILE, STACK, TEMPLATE


class TestCreate(unittest.TestCase):
    def run_create(self, exit_code=0):
        runner = CliRunner()
        result = runner.invoke(cli.create,
                               ['--stack',
                                STACK,
                                '--profile',
                                PROFILE,
                                '--region',
                                REGION])
        if result.exit_code != exit_code:
            print(result.output)
            print(result.exception)
            print(result.exit_code)
        self.assertEquals(result.exit_code, exit_code)
        return result

    @patch('formica.cli.AWSSession')
    def test_create_uses_parameters_for_session(self, session):
        self.run_create(0)
        session.assert_called_with(REGION, PROFILE)

    @patch('formica.cli.AWSSession')
    def test_create_gets_cloudformation_client(self, session):
        self.run_create(0)
        session.return_value.client_for.assert_called_with('cloudformation')

    @patch('formica.cli.AWSSession')
    def test_does_not_call_create_if_stack_exists(self, session):
        cf_client_mock = Mock()
        session.return_value.client_for.return_value = cf_client_mock
        self.run_create(0)
        cf_client_mock.describe_stacks.assert_called_with(StackName=STACK)
        cf_client_mock.create_stack.assert_not_called()

    @patch('formica.cli.AWSSession')
    @patch('formica.create.Loader')
    def test_reraises_without_creating_stack(self, loader, session):
        cf_client_mock = Mock()
        session.return_value.client_for.return_value = cf_client_mock
        exception = botocore.exceptions.ClientError(dict(Error=dict(
            Code='SomeOtherError')), "DescribeStacks")
        cf_client_mock.describe_stacks.side_effect = exception
        result = self.run_create(-1)
        self.assertEquals(result.exception, exception)
        loader.assert_not_called()
        cf_client_mock.create_stack.assert_not_called()

    @patch('formica.cli.AWSSession')
    @patch('formica.create.Loader')
    def test_creates_stack_from_template__and_waits(self, loader, session):
        cf_client_mock = Mock()

        session.return_value.client_for.return_value = cf_client_mock
        exception = botocore.exceptions.ClientError(dict(Error=dict(
            Code='ValidationError')), "DescribeStacks")
        cf_client_mock.describe_stacks.side_effect = exception

        loader.return_value.template.return_value = TEMPLATE

        self.run_create(0)
        loader.return_value.load.assert_called_with()
        cf_client_mock.create_stack.assert_called_with(
            StackName=STACK, TemplateBody=TEMPLATE)

        cf_client_mock.get_waiter.assert_called_with('stack_create_complete')
        cf_client_mock.get_waiter.return_value.wait.assert_called_with(
            StackName=STACK)
