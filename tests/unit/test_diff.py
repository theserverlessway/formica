import pytest
import re
import yaml
from formica import cli

from formica.diff import compare
from tests.unit.constants import STACK


@pytest.fixture
def client(session, mocker):
    client_mock = mocker.Mock()
    session.return_value.client.return_value = client_mock
    return client_mock


@pytest.fixture
def session(mocker):
    return mocker.patch('boto3.session.Session')


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


def check_echo(logger, args):
    regex = '\\s+\\|\\s+'.join(args)
    assert re.search(regex, logger.info.call_args[0][0])


@pytest.fixture
def logger(mocker):
    return mocker.patch('formica.diff.logger')


def test_unicode_string_no_diff(loader, client, logger):
    loader_return(loader, {'Resources': u'1234'})
    compare({'Resources': '1234'})
    logger.info.assert_called_with('No Changes found')


def test_values_changed(loader, client, logger):
    loader_return(loader, {'Resources': '5678'})
    compare({'Resources': '1234'})
    check_echo(logger, ['Resources', '1234', '5678', 'Values Changed'])


def test_dictionary_item_added(loader, client, logger):
    loader_return(loader, {'Resources': '5678'})
    compare({})
    check_echo(logger, ['Resources', 'Not Present', '5678', 'Dictionary Item Added'])


def test_dictionary_item_removed(loader, client, logger):
    loader_return(loader, {})
    compare({'Resources': '5678'})
    check_echo(logger, ['Resources', '5678', 'Not Present', 'Dictionary Item Removed'])


def test_type_changed(loader, client, logger):
    loader_return(loader, {'Resources': 5})
    compare({'Resources': 'abcde'})
    check_echo(logger, ['Resources', 'abcde', '5', 'Type Changes'])


def test_iterable_item_added(loader, client, logger):
    loader_return(loader, {'Resources': [1, 2]})
    compare({'Resources': [1]})
    check_echo(logger, ['Resources > 1', 'Not Present', '2', 'Iterable Item Added'])


def test_iterable_item_removed(loader, client, logger):
    loader_return(loader, {'Resources': [1]})
    compare({'Resources': [1, 2]})
    check_echo(logger, ['Resources > 1', '2', 'Not Present', 'Iterable Item Removed'])


def test_request_returns_string(loader, client, logger):
    loader_return(loader, {'Resources': u'1234'})
    compare(yaml.dump({'Resources': '1234'}))
    logger.info.assert_called_with('No Changes found')


def test_diff_cli_call(template, mocker, client):
    diff = mocker.patch('formica.diff.compare')
    cli.main(['diff', '--stack', STACK])
    client.get_template.assert_called_with(StackName=STACK)
    diff.assert_called_with(template, mocker.ANY)


def test_diff_cli_with_vars(template, mocker):
    diff = mocker.patch('formica.diff.compare')
    cli.main(['diff', '--stack', STACK, '--vars', 'abc=def'])
    diff.assert_called_with(template, {'abc': 'def'})
