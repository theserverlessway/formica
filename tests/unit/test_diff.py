import json

import pytest
import yaml
from formica import cli
from uuid import uuid4

from formica.diff import compare_stack, compare_stack_set
from tests.unit.constants import STACK


@pytest.fixture
def client(aws_client):
    aws_client.get_template.return_value = {'TemplateBody': template}
    aws_client.describe_stacks.return_value = {'Stacks': [{}]}
    return aws_client


@pytest.fixture
def loader(mocker):
    return mocker.patch('formica.diff.Loader')


@pytest.fixture
def template(client, mocker):
    template = mocker.Mock()
    client.get_template.return_value = {'TemplateBody': template}
    return template


def loader_return(loader, template):
    loader.return_value.template_dictionary.return_value = template


def template_return(client, template):
    client.get_template.return_value = {'TemplateBody': json.dumps(template)}


def check_echo(caplog, args):
    assert all([arg in caplog.text for arg in args])


def check_no_echo(caplog, args):
    assert not any([arg in caplog.text for arg in args])


def uuid():
    return str(uuid4())


def test_loads_stack_data(client, loader, mocker):
    compare_stack(STACK)
    client.get_template.assert_called_with(StackName=STACK)
    client.describe_stacks.assert_called_with(StackName=STACK)


def test_loads_stack_set_data(client, loader):
    client.describe_stack_set.return_value = {'StackSet': {'TemplateBody': ''}}
    compare_stack_set(STACK)
    client.describe_stack_set.assert_called_with(StackSetName=STACK)


def test_unicode_string_no_diff(loader, client, caplog):
    loader_return(loader, {'Resources': u'1234'})
    template_return(client, {'Resources': '1234'})
    compare_stack(STACK)
    check_no_echo(caplog, ['1234'])


def test_values_changed(loader, client, caplog):
    loader_return(loader, {'Resources': '5678'})
    template_return(client, {'Resources': '1234'})
    compare_stack(STACK)
    check_echo(caplog, ['Resources', '1234', '5678', 'Values Changed'])


def test_dictionary_item_added(loader, client, caplog):
    loader_return(loader, {'Resources': '5678'})
    template_return(client, {})
    compare_stack(STACK)
    check_echo(caplog, ['Resources', 'Not Present', '5678', 'Dictionary Item Added'])


def test_dictionary_item_removed(loader, client, caplog):
    loader_return(loader, {})
    template_return(client, {'Resources': '5678'})
    compare_stack(STACK)
    check_echo(caplog, ['Resources', '5678', 'Not Present', 'Dictionary Item Removed'])


def test_type_changed(loader, client, caplog):
    loader_return(loader, {'Resources': 5})
    template_return(client, {'Resources': 'abcde'})
    compare_stack(STACK)
    check_echo(caplog, ['Resources', 'abcde', '5', 'Type Changes'])


def test_iterable_item_added(loader, client, caplog):
    loader_return(loader, {'Resources': [1, 2]})
    template_return(client, {'Resources': [1]})
    compare_stack(STACK)
    check_echo(caplog, ['Resources > 1', 'Not Present', '2', 'Iterable Item Added'])


def test_iterable_item_removed(loader, client, caplog):
    loader_return(loader, {'Resources': [1]})
    template_return(client, {'Resources': [1, 2]})
    compare_stack(STACK)
    check_echo(caplog, ['Resources > 1', '2', 'Not Present', 'Iterable Item Removed'])


def test_request_returns_string(loader, client, caplog):
    loader_return(loader, {'Resources': u'1234'})
    client.get_template.return_value = {'TemplateBody': yaml.dump({'Resources': '1234'})}
    compare_stack(STACK)
    check_no_echo(caplog, ['1234'])


def test_long_numbers(loader, client, caplog):
    id1 = '987497529474523452345234'
    id2 = '235462563563456345634563'
    loader_return(loader, {'Resources': id1})
    client.get_template.return_value = {'TemplateBody': yaml.dump({'Resources': id2})}
    compare_stack(STACK)
    check_echo(caplog, [id1, id2])


def test_diff_cli_with_vars(template, mocker):
    diff = mocker.patch('formica.diff.compare_stack')
    cli.main(['diff', '--stack', STACK, '--vars', 'V=1', '--parameters', 'P=2', '--tags', 'T=3'])
    diff.assert_called_with(stack=STACK, vars={'V': '1'}, parameters={'P': '2'}, tags={'T': '3'})


def test_diff_parameters(caplog, loader, client):
    key = uuid()
    before = uuid()
    after = uuid()
    loader_return(loader, {'Resources': u'1234'})
    client.get_template.return_value = {'TemplateBody': yaml.dump({'Resources': '1234'})}
    client.describe_stacks.return_value = {
        'Stacks': [{'Parameters': [{'ParameterKey': key, 'ParameterValue': before}]}]}
    compare_stack(STACK, parameters={key: after})
    check_echo(caplog, [key, before, after, 'Values Changed'])


def test_diff_parameters_overrides_defaults(caplog, loader, client):
    key = uuid()
    before = uuid()
    after = uuid()
    key2 = uuid()
    template = {'Resources': '1234', 'Parameters': {key: {'Default': after}, key2: {'Default': after}}}
    loader_return(loader, template)
    client.get_template.return_value = {'TemplateBody': json.dumps(template)}
    client.describe_stacks.return_value = {
        'Stacks': [{'Parameters': [{'ParameterKey': key, 'ParameterValue': before},
                                   {'ParameterKey': key2, 'ParameterValue': before}]}]}
    compare_stack(STACK, parameters={key2: before})
    check_echo(caplog, [key, before, after, 'Values Changed'])
    check_no_echo(caplog, [key2])


def test_diff_tags(caplog, loader, client):
    key = uuid()
    before = uuid()
    after = uuid()
    loader_return(loader, {'Resources': u'1234'})
    client.get_template.return_value = {'TemplateBody': yaml.dump({'Resources': '1234'})}
    client.describe_stacks.return_value = {
        'Stacks': [{'Tags': [{'Key': key, 'Value': before}]}]}
    compare_stack(STACK, tags={key: after})
    check_echo(caplog, [key, before, after, 'Values Changed'])


def test_diff__on_stack_set(caplog, loader, client):
    template = (uuid(), uuid())
    tag_key = uuid()
    tag_before = uuid()
    tag_after = uuid()
    parameter_key = uuid()
    parameter_before = uuid()
    parameter_after = uuid()
    loader_return(loader, {'Resources': template[0]})
    client.get_template.return_value = {}
    client.describe_stack_set.return_value = {
        'StackSet': {
            'Parameters': [{'ParameterKey': parameter_key, 'ParameterValue': parameter_before}],
            'Tags': [{'Key': tag_key, 'Value': tag_before}],
            'TemplateBody': yaml.dump({'Resources': template[1]})
        }
    }
    compare_stack_set(STACK, parameters={parameter_key: parameter_after}, tags={tag_key: tag_after})
    check_echo(caplog, [parameter_key, parameter_before, parameter_after, 'Values Changed'])
    check_echo(caplog, [tag_key, tag_before, tag_after, 'Values Changed'])
    check_echo(caplog, ['Resources', template[0], template[1], 'Values Changed'])
    check_no_echo(caplog, ['No Changes found'])
