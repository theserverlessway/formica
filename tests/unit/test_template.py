import json
import os
import yaml
import pytest
from path import Path

from formica import cli
from .constants import ACCOUNTS, EC2_REGIONS


@pytest.fixture
def logger(mocker):
    return mocker.patch('formica.cli.logger')


def test_template_calls_template(tmpdir, logger):
    with Path(tmpdir):
        with open('test.template.json', 'w') as f:
            f.write('{"Description": "{{ \'test\' | title }}"}')
        cli.main(['template'])
        logger.info.assert_called()
        assert {"Description": "Test"} == json.loads(logger.info.call_args[0][0])


def test_template_calls_template_with_yaml(tmpdir, logger):
    with Path(tmpdir):
        with open('test.template.json', 'w') as f:
            f.write('{"Description": "{{ \'test\' | title }}"}')
        cli.main(['template', '--yaml'])
        logger.info.assert_called()
        assert {"Description": "Test"} == yaml.load(logger.info.call_args[0][0])


def test_with_organization_variables(aws_client, aws_session, tmpdir, logger):
    aws_client.list_accounts.return_value = ACCOUNTS
    aws_client.describe_regions.return_value = EC2_REGIONS
    aws_client.get_caller_identity.return_value = {'Account': '1234'}
    example = '{"Resources": {"ModuleAccounts": {{ AWSAccounts | tojson }}, "ModuleSubAccounts": {{ AWSSubAccounts | tojson }}, "ModuleRegions": {{ AWSRegions | tojson }}, "ModuleMainAccount": {{ AWSMainAccount | tojson }}}}'
    with Path(tmpdir):
        os.mkdir('moduledir')
        with open('moduledir/test.template.json', 'w') as f:
            f.write(example)
        with open('test.template.json', 'w') as f:
            f.write(
                '{"Resources": {"AccountsRegionsTest": {"From": "Moduledir"}, "Accounts": {{ AWSAccounts | tojson}}, "SubAccounts": {{ AWSSubAccounts | tojson}}, "Regions": {{ AWSRegions | tojson }} }}')
        cli.main(['template', '--organization-variables'])
        logger.info.assert_called()
        output = logger.info.call_args[0][0]

        actual = yaml.load(output)
        expected = {'Resources': {'Accounts': [{'Email': 'email1@test.com', 'Id': '1234', 'Name': 'TestName1'},
                                               {'Email': 'email2@test.com', 'Id': '5678', 'Name': 'TestName2'}],
                                  'SubAccounts': [{'Email': 'email2@test.com', 'Id': '5678', 'Name': 'TestName2'}],
                                  'ModuleAccounts': [{'Email': 'email1@test.com', 'Id': '1234', 'Name': 'TestName1'},
                                                     {'Email': 'email2@test.com', 'Id': '5678', 'Name': 'TestName2'}],
                                  'ModuleSubAccounts': [
                                      {'Email': 'email2@test.com', 'Id': '5678', 'Name': 'TestName2'}],
                                  'ModuleMainAccount': {'Email': 'email1@test.com',
                                                        'Id': '1234',
                                                        'Name': 'TestName1'},
                                  'ModuleRegions': ['us-west-1', 'us-west-2'], 'Regions': ['us-west-1', 'us-west-2']}}
    assert actual == expected
