import pytest
from formica import cli
from botocore.exceptions import ProfileNotFound, NoCredentialsError, NoRegionError, ClientError

from tests.unit.constants import STACK, MESSAGE

METHODS = ['change', 'deploy', 'new', 'remove', 'resources']
NO_STACK_METHODS = ['stacks']

Exceptions = [ProfileNotFound, NoCredentialsError, NoRegionError, ClientError]


# @patch('formica.cli.print')
# @patch('formica.helper.sys')
# def test_catches_common_aws_exceptions(sys):
#     for e in [ProfileNotFound, NoCredentialsError, NoRegionError]:
#         def testfunction():
#             raise e(profile='test')

#     sys.exit.assert_called_with(1)
#     self.assertEquals(3, sys.exit.call_count)


@pytest.fixture
def session(mocker):
    return mocker.patch('formica.aws.Session')


@pytest.fixture
def logger(mocker):
    return mocker.patch('formica.cli.logger')


def test_commands_use_exception_handling(session, logger):
    session.side_effect = NoCredentialsError()
    for method in METHODS:
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            cli.main([method, '--stack', STACK])
        assert pytest_wrapped_e.value.code == 1

    for method in NO_STACK_METHODS:
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            cli.main([method])
        assert pytest_wrapped_e.value.code == 1


def test_catches_client_errors(session, logger):
    session.side_effect = ClientError({'Error': {'Code': 'ValidationError', 'Message': MESSAGE}}, 'ERROR_TEST')
    for method in METHODS:
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            cli.main([method, '--stack', STACK])
        logger.info.assert_called_with(MESSAGE)
        assert pytest_wrapped_e.value.code == 1

    for method in NO_STACK_METHODS:
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            cli.main([method])
        assert pytest_wrapped_e.value.code == 1


def test_arbitrary_clients_error(session, logger):
    error = ClientError({'Error': {'Code': 'SOMEOTHER', 'Message': MESSAGE}}, 'ERROR_TEST')
    session.side_effect = error
    for method in METHODS:
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            cli.main([method, '--stack', STACK])
        assert pytest_wrapped_e.value.code == 2
        logger.info.assert_called_with(error)

    for method in NO_STACK_METHODS:
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            cli.main([method])
        assert pytest_wrapped_e.value.code == 2
