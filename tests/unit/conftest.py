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
def boto_resource(mocker):
    return mocker.patch('boto3.resource')

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


@pytest.fixture
def uuid4(mocker):
    return mocker.patch('uuid.uuid4')

@pytest.fixture
def temp_bucket(mocker):
    t = mocker.patch('formica.helper.temporary_bucket')
    tempbucket_mock = mocker.Mock()
    t.return_value.__enter__.return_value = tempbucket_mock
    return tempbucket_mock

@pytest.fixture
def temp_bucket_cli(mocker):
    t = mocker.patch('formica.cli.temporary_bucket')
    tempbucket_mock = mocker.Mock()
    t.return_value.__enter__.return_value = tempbucket_mock
    return tempbucket_mock