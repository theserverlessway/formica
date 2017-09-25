import pytest
import re
import yaml
from formica import cli

from formica.diff import Diff
from tests.unit.constants import STACK


@pytest.fixture
def client(mocker):
    return mocker.Mock()


@pytest.fixture
def session(client, mocker):
    mock = mocker.Mock()
    mock.client.return_value = client
    return mock


@pytest.fixture
def diff(session):
    return Diff(session)


@pytest.fixture
def loader(mocker):
    return mocker.patch('formica.diff.Loader')


def template_return(client, template):
    client.get_template.return_value = {'TemplateBody': template}


def loader_return(loader, template):
    loader.return_value.template_dictionary.return_value = template


def check_echo(logger, args):
    regex = '\s+\|\s+'.join(args)
    assert re.search(regex, logger.info.call_args[0][0])


@pytest.fixture
def logger(mocker):
    return mocker.patch('formica.diff.logger')


def test_unicode_string_no_diff(loader, client, diff, logger):
    loader_return(loader, {'Resources': u'1234'})
    template_return(client, {'Resources': '1234'})
    diff.run(STACK)
    logger.info.assert_called_with('No Changes found')


def test_values_changed(loader, client, diff, logger):
    template_return(client, {'Resources': '1234'})
    loader_return(loader, {'Resources': '5678'})
    diff.run(STACK)
    check_echo(logger, ['Resources', '1234', '5678', 'Values Changed'])


def test_dictionary_item_added(loader, client, diff, logger):
    loader_return(loader, {'Resources': '5678'})
    template_return(client, {})
    diff.run(STACK)
    check_echo(logger, ['Resources', 'Not Present', '5678', 'Dictionary Item Added'])


def test_dictionary_item_removed(loader, client, diff, logger):
    loader_return(loader, {})
    template_return(client, {'Resources': '5678'})
    diff.run(STACK)
    check_echo(logger, ['Resources', '5678', 'Not Present', 'Dictionary Item Removed'])


def test_type_changed(loader, client, diff, logger):
    template_return(client, {'Resources': 'abcde'})
    loader_return(loader, {'Resources': 5})
    diff.run(STACK)
    check_echo(logger, ['Resources', 'abcde', '5', 'Type Changes'])


def test_iterable_item_added(loader, client, diff, logger):
    template_return(client, {'Resources': [1]})
    loader_return(loader, {'Resources': [1, 2]})
    diff.run(STACK)
    check_echo(logger, ['Resources > 1', 'Not Present', '2', 'Iterable Item Added'])


def test_iterable_item_removed(loader, client, diff, logger):
    template_return(client, {'Resources': [1, 2]})
    loader_return(loader, {'Resources': [1]})
    diff.run(STACK)
    check_echo(logger, ['Resources > 1', '2', 'Not Present', 'Iterable Item Removed'])


def test_request_returns_string(loader, client, diff, logger):
    loader_return(loader, {'Resources': u'1234'})
    template_return(client, yaml.dump({'Resources': '1234'}))
    diff.run(STACK)
    logger.info.assert_called_with('No Changes found')


def test_diff_cli_call(mocker, session):
    aws = mocker.patch('formica.cli.AWS')
    aws.current_session.return_value = session
    print(session)

    diff = mocker.patch('formica.cli.Diff')

    cli.main(['diff', '--stack', STACK])

    diff.assert_called_with(session)
    diff.return_value.run.assert_called_with(STACK, mocker.ANY)


def test_diff_cli_with_vars(mocker, session):
    aws = mocker.patch('formica.cli.AWS')
    aws.current_session.return_value = session
    print(session)

    diff = mocker.patch('formica.cli.Diff')

    cli.main(['diff', '--stack', STACK, '--vars', 'abc=def'])

    diff.assert_called_with(session)
    diff.return_value.run.assert_called_with(STACK, {'abc': 'def'})
