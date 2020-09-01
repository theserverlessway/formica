import pytest
from formica import cli, __version__
from botocore.exceptions import ProfileNotFound, NoCredentialsError, NoRegionError, ClientError

from tests.unit.constants import STACK, MESSAGE

METHODS = ['change', 'deploy', 'new', 'remove', 'resources']
NO_STACK_METHODS = ['stacks']

Exceptions = [ProfileNotFound, NoCredentialsError, NoRegionError, ClientError]


@pytest.fixture
def logger(mocker):
    return mocker.patch('formica.cli.logger')

def test_fails_for_no_arguments(capsys):
    with pytest.raises(SystemExit):
        cli.main([])
    out, err = capsys.readouterr()
    assert 'usage:' in err


def test_prints_version(capsys):
    with pytest.raises(SystemExit):
        cli.main(['--version'])
    out = "\n".join(capsys.readouterr())
    assert __version__ in out


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


def test_catches_arbitrary_client_error(session, logger):
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


def test_fails_with_wrong_parameter_format(capsys):
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        cli.main(['new', '--stack', STACK, '--parameters', 'Test:Test'])
    out, err = capsys.readouterr()
    assert "argument --parameters: Test:Test needs to be in format KEY=VALUE" in err
    assert pytest_wrapped_e.value.code == 2
