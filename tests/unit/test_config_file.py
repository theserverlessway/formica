import pytest
from path import Path
import yaml
from formica import cli
from tests.unit.constants import (REGION, PROFILE, STACK,
                                  CHANGE_SET_PARAMETERS, CHANGE_SET_STACK_TAGS,
                                  FULL_CONFIG_FILE, CHANGE_SET_CAPABILITIES,
                                  ROLE_ARN)


@pytest.fixture
def session(mocker):
    return mocker.patch('formica.aws.Session')


@pytest.fixture
def logger(mocker):
    return mocker.patch('formica.cli.logger')


def test_loads_config_file(mocker, tmpdir, session):
    stacks = mocker.patch('formica.cli.stacks')
    file_name = 'test.config.yaml'
    with Path(tmpdir):
        with open(file_name, 'w') as f:
            f.write(yaml.dump(FULL_CONFIG_FILE))
        cli.main(['stacks', '-c', file_name])
        call_args = stacks.call_args[0][0]
        assert call_args.region == REGION
        assert call_args.profile == PROFILE
        assert call_args.stack == STACK
        assert call_args.parameters == CHANGE_SET_PARAMETERS
        assert call_args.tags == CHANGE_SET_STACK_TAGS
        assert call_args.capabilities == CHANGE_SET_CAPABILITIES
        assert call_args.role_arn == ROLE_ARN


def test_exception_with_wrong_config_type(mocker, tmpdir, session, logger):
    file_name = 'test.config.yaml'
    with Path(tmpdir):
        with open(file_name, 'w') as f:
            f.write(yaml.dump({'stack': ['test', 'test2']}))
        with pytest.raises(SystemExit):
            cli.main(['stacks', '-c', file_name])
        logger.error.assert_called_with('Config file parameter stack needs to be of type str')


def test_exception_with_forbiddeng_config_argument(mocker, tmpdir, session, logger):
    file_name = 'test.config.yaml'
    with Path(tmpdir):
        with open(file_name, 'w') as f:
            f.write(yaml.dump({'stacks': 'somestack'}))
        with pytest.raises(SystemExit):
            cli.main(['stacks', '-c', file_name])
        logger.error.assert_called_with('Config file parameter stacks is not supported')


def test_exception_with_failed_yaml_syntax(mocker, tmpdir, session, logger):
    file_name = 'test.config.yaml'
    with Path(tmpdir):
        with open(file_name, 'w') as f:
            f.write("stacks: somestack\nprofile testprofile")
        with pytest.raises(SystemExit):
            cli.main(['stacks', '-c', file_name])
        logger.error.assert_called()
