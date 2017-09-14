import pytest
from path import Path
import yaml
from formica import cli
from tests.unit.constants import (REGION, PROFILE, STACK,
                                  CHANGE_SET_PARAMETERS, CHANGE_SET_STACK_TAGS,
                                  FULL_CONFIG_FILE, CHANGE_SET_CAPABILITIES)


@pytest.fixture
def session(mocker):
    return mocker.patch('formica.aws.Session')


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
