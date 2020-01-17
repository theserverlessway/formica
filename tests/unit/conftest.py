import pytest


@pytest.fixture
def botocore_session(mocker):
    return mocker.patch('botocore.session.Session')


@pytest.fixture
def session(mocker, botocore_session):
    return mocker.patch('boto3.session.Session')


@pytest.fixture
def aws_session(mocker):
    return mocker.patch('formica.aws.AWS.current_session')


@pytest.fixture
def aws_client(aws_session, mocker):
    client_mock = mocker.Mock()
    aws_session.return_value.client.return_value = client_mock
    return client_mock


@pytest.fixture
def client(session, mocker):
    client_mock = mocker.Mock()
    session.return_value.client.return_value = client_mock
    return client_mock


@pytest.fixture
def logger(mocker):
    return mocker.patch('formica.cli.logger')


@pytest.fixture
def loader(mocker):
    return mocker.patch('formica.loader.Loader')


@pytest.fixture
def change_set(mocker):
    return mocker.patch('formica.change_set.ChangeSet')


@pytest.fixture
def stack_waiter(mocker):
    return mocker.patch('formica.stack_waiter.StackWaiter')

@pytest.fixture
def paginators(mocker):
    def mock_paginate(**kwargs):
        def sideeffect(paginator):
            m = mocker.Mock()
            m.paginate.return_value = kwargs.get(paginator)
            return m
        return sideeffect

    return mock_paginate