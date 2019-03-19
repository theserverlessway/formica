import pytest


@pytest.fixture
def session(mocker):
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
