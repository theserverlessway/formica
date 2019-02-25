import pytest
from path import Path
import yaml
from uuid import uuid4
from formica import cli
from tests.unit.constants import (REGION, PROFILE, STACK,
                                  CHANGE_SET_PARAMETERS, CHANGE_SET_STACK_TAGS,
                                  FULL_CONFIG_FILE, CHANGE_SET_CAPABILITIES,
                                  ROLE_ARN, VARS)


@pytest.fixture
def session(mocker):
    return mocker.patch('boto3.session.Session')


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
        assert call_args.vars == VARS


def test_loads_multiple_config_files(mocker, tmpdir, session):
    stacks = mocker.patch('formica.cli.stacks')
    file_name = 'test.config.yaml'
    overwrite_file = 'overwrite.config.yaml'
    with Path(tmpdir):
        with open(file_name, 'w') as f:
            f.write(yaml.dump(FULL_CONFIG_FILE))
        with open(overwrite_file, 'w') as f:
            f.write(yaml.dump(dict(stack='someotherstacktestvalue', vars=dict(OtherVar=3))))
        cli.main(['stacks', '-c', file_name, overwrite_file])
        call_args = stacks.call_args[0][0]
        assert call_args.stack == 'someotherstacktestvalue'
        assert call_args.stack != STACK
        assert call_args.vars['OtherVar'] == 3
        assert call_args.vars['OtherVar'] != VARS['OtherVar']


def test_prioritises_cli_args(mocker, tmpdir, session):
    stacks = mocker.patch('formica.cli.new')
    cli_stack = str(uuid4())
    file_name = 'test.config.yaml'
    with Path(tmpdir):
        with open(file_name, 'w') as f:
            f.write(yaml.dump(FULL_CONFIG_FILE))
        cli.main(['new', '-s', cli_stack, '-c', file_name])
        call_args = stacks.call_args[0][0]
        assert call_args.stack == cli_stack
        assert call_args.stack != STACK


def test_merges_cli_args_on_load(mocker, tmpdir, session):
    stacks = mocker.patch('formica.cli.new')
    param1 = str(uuid4())
    param2 = str(uuid4())
    file_name = 'test.config.yaml'
    with Path(tmpdir):
        with open(file_name, 'w') as f:
            f.write(yaml.dump(FULL_CONFIG_FILE))
        cli.main(['new', '--parameters', "A={}".format(param1), "D={}".format(param2), '-c', file_name])
        call_args = stacks.call_args[0][0]
        assert call_args.parameters == {"A": param1, "B": 2, 'C': True, 'D': param2}


def test_merges_vars(mocker, tmpdir, session):
    stacks = mocker.patch('formica.cli.template')
    param1 = str(uuid4())
    file_name = 'test.config.yaml'
    with Path(tmpdir):
        with open(file_name, 'w') as f:
            f.write(yaml.dump(FULL_CONFIG_FILE))
        with open('test.template.yaml', 'w') as f:
            f.write('{"Description": "{{ OtherVar }}"}')
        cli.main(['template', '--vars', "OtherVar={}".format(param1), '-c', file_name])
        call_args = stacks.call_args[0][0]
        assert call_args.vars['OtherVar'] == param1


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


def test_loads_empty_config_file(mocker, tmpdir, session):
    stacks = mocker.patch('formica.cli.stacks')
    file_name = 'test.config.yaml'
    with Path(tmpdir):
        with open(file_name, 'w') as f:
            f.write('')
        cli.main(['stacks', '-c', file_name])
