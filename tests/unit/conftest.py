import pytest


@pytest.fixture
def botocore_session(mocker):
    return mocker.patch('botocore.session.Session')


@pytest.fixture
def session(botocore_session):
    return botocore_session


@pytest.fixture
def boto_client(mocker):
    mocker.patch('formica.aws.boto3')
    mocker.patch('formica.aws.botocore')
    return mocker.patch('boto3.client')

@pytest.fixture
def aws_client(boto_client, mocker):
    client_mock = mocker.Mock()
    boto_client.return_value = client_mock
    return client_mock


@pytest.fixture
def client(aws_client):
    return aws_client


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