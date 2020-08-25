import pytest

from formica import aws
from tests.unit.constants import REGION, PROFILE


@pytest.fixture
def boto(mocker):
    return mocker.patch('formica.aws.boto3')


def test_init_without_parameters(boto, session, botocore_session, mocker):
    region = 'region'
    profile = 'profile'
    session_mock = mocker.Mock()
    botocore_session.return_value = session_mock

    aws.initialize(region, profile)
    botocore_session.assert_called_with(profile=profile)

    boto.setup_default_session.assert_called_with(botocore_session=session_mock, region_name=region, profile_name=profile)
