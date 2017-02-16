
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from unittest import TestCase
from mock import patch

from botocore.exceptions import ProfileNotFound, NoCredentialsError, NoRegionError, ClientError
from click.testing import CliRunner

from formica.cli import change, deploy, new, stacks, remove
from formica.helper import aws_exceptions
from tests.unit.constants import STACK, MESSAGE

METHODS = [change, deploy, new, remove]
NO_STACK_METHODS = [stacks]


class TestCLI(TestCase):
    @patch('formica.helper.sys')
    def test_catches_common_aws_exceptions(self, sys):
        for e in [ProfileNotFound, NoCredentialsError, NoRegionError]:
            def testfunction():
                raise e(profile='test')

            aws_exceptions(testfunction)()

        sys.exit.assert_called_with(1)
        self.assertEquals(3, sys.exit.call_count)

    @patch('formica.aws.Session')
    def test_commands_use_exception_handling(self, session):
        session.side_effect = NoCredentialsError()
        runner = CliRunner()
        for method in METHODS:
            result = runner.invoke(method, ['--stack', STACK])
            self.assertEqual(result.exit_code, 1)

        for method in NO_STACK_METHODS:
            result = runner.invoke(method)
            self.assertEqual(result.exit_code, 1)

    @patch('formica.helper.click')
    @patch('formica.aws.Session')
    def test_catches_client_errors(self, session, click):
        session.side_effect = ClientError({'Error': {'Code': 'ValidationError', 'Message': MESSAGE}}, 'ERROR_TEST')
        runner = CliRunner()
        for method in METHODS:
            result = runner.invoke(method, ['--stack', STACK])
            self.assertEqual(result.exit_code, 1)
            click.echo.assert_called_with(MESSAGE)

        for method in NO_STACK_METHODS:
            result = runner.invoke(method)
            self.assertEqual(result.exit_code, 1)
            click.echo.assert_called_with(MESSAGE)

    @patch('formica.helper.click')
    @patch('formica.aws.Session')
    def test_arbitrary_clients_error(self, session, click):
        session.side_effect = ClientError({'Error': {'Code': 'SOMEOTHER', 'Message': MESSAGE}}, 'ERROR_TEST')
        runner = CliRunner()
        for method in METHODS:
            result = runner.invoke(method, ['--stack', STACK])
            self.assertEqual(result.exit_code, 2)

        for method in NO_STACK_METHODS:
            result = runner.invoke(method)
            self.assertEqual(result.exit_code, 2)
