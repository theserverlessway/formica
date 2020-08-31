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
        assert {"Description": "Test"} == yaml.safe_load(logger.info.call_args[0][0])


def test_with_organization_variables(aws_client, tmpdir, logger, paginators):
    aws_client.get_paginator.side_effect = paginators(list_accounts=[ACCOUNTS])
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

        actual = yaml.safe_load(output)
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


def test_with_organization_region_variables_no_account_variables(aws_client, tmpdir, logger, paginators):
    aws_client.get_paginator.side_effect = paginators(list_accounts=[ACCOUNTS])
    aws_client.describe_regions.return_value = EC2_REGIONS
    aws_client.get_caller_identity.return_value = {'Account': '1234'}
    example = '{"Resources": {"Accounts": {{ AWSAccounts | tojson }}, "SubAccounts": {{ AWSSubAccounts | tojson }}, "Regions": {{ AWSRegions | tojson }}, "MainAccount": {{ AWSMainAccount | tojson }}}}'
    with Path(tmpdir):
        with open('test.template.json', 'w') as f:
            f.write(example)

        # CLI now raises a TypeError because {{AWSAccounts}} and other account variables are null and cannot be json-serialized
        with pytest.raises(TypeError):
            cli.main(['template', '--organization-region-variables'])


def test_with_organization_region_variables(aws_client, tmpdir, logger, paginators):
    aws_client.get_paginator.side_effect = paginators(list_accounts=[ACCOUNTS])
    aws_client.describe_regions.return_value = EC2_REGIONS
    aws_client.get_caller_identity.return_value = {'Account': '1234'}
    example = '{"Resources": {"Regions": {{ AWSRegions | tojson }}}}'
    with Path(tmpdir):
        with open('test.template.json', 'w') as f:
            f.write(example)

        cli.main(['template', '--organization-region-variables'])
        logger.info.assert_called()
        output = logger.info.call_args[0][0]

        actual = yaml.safe_load(output)
        expected = {'Resources': {'Regions': ['us-west-1', 'us-west-2'], 'Regions': ['us-west-1', 'us-west-2']}}
    assert actual == expected


def test_with_organization_account_variables_no_region_variables(aws_client, tmpdir, logger, paginators):
    aws_client.get_paginator.side_effect = paginators(list_accounts=[ACCOUNTS])
    aws_client.describe_regions.return_value = EC2_REGIONS
    aws_client.get_caller_identity.return_value = {'Account': '1234'}
    example = '{"Resources": {"Accounts": {{ AWSAccounts | tojson }}, "SubAccounts": {{ AWSSubAccounts | tojson }}, "Regions": {{ AWSRegions | tojson }}, "MainAccount": {{ AWSMainAccount | tojson }}}}'
    with Path(tmpdir):
        with open('test.template.json', 'w') as f:
            f.write(example)

        # CLI now raises a TypeError because {{AWSRegions}} is null and cannot be json-serialized
        with pytest.raises(TypeError):
            cli.main(['template', '--organization-account-variables'])


def test_with_organization_account_variables(aws_client, tmpdir, logger, paginators):
    aws_client.get_paginator.side_effect = paginators(list_accounts=[ACCOUNTS])
    aws_client.describe_regions.return_value = EC2_REGIONS
    aws_client.get_caller_identity.return_value = {'Account': '1234'}
    example = '{"Resources": {"Accounts": {{ AWSAccounts | tojson }}, "SubAccounts": {{ AWSSubAccounts | tojson }}, "MainAccount": {{ AWSMainAccount | tojson }}}}'
    with Path(tmpdir):
        with open('test.template.json', 'w') as f:
            f.write(example)

        cli.main(['template', '--organization-account-variables'])
        logger.info.assert_called()
        output = logger.info.call_args[0][0]

        actual = yaml.safe_load(output)
        expected = {'Resources': {'Accounts': [{'Email': 'email1@test.com', 'Id': '1234', 'Name': 'TestName1'},
                                               {'Email': 'email2@test.com', 'Id': '5678', 'Name': 'TestName2'}],
                                  'SubAccounts': [{'Email': 'email2@test.com', 'Id': '5678', 'Name': 'TestName2'}],
                                  'MainAccount': {'Email': 'email1@test.com', 'Id': '1234', 'Name': 'TestName1'}}}
    assert actual == expected


def test_with_artifacts(aws_client, tmpdir, logger, paginators):
    aws_client.get_paginator.side_effect = paginators(list_accounts=[ACCOUNTS])
    aws_client.describe_regions.return_value = EC2_REGIONS
    aws_client.meta.region_name = "eu-central-1"
    aws_client.get_caller_identity.return_value = {'Account': '1234'}
    example = '{"Resources": {"Bucket": {{ artifacts["bucketfile"].bucket }}, "Key": {{ artifacts["bucketfile"].key }} }}'
    with Path(tmpdir):
        with open('test.template.json', 'w') as f:
            f.write(example)
        with open('bucketfile', 'w') as f:
            f.write("Testfile")

        cli.main(['template', '--artifacts', 'bucketfile'])
        logger.info.assert_called()
        output = logger.info.call_args[0][0]

        actual = yaml.safe_load(output)
        expected = {"Resources": {"Bucket": "formica-deploy-83acc03037c35fdce1aae77faa87d9f2", "Key": "864c71d530a42421476458005e05b2a0" }}
    assert actual == expected
