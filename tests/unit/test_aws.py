import pytest

from formica.aws import AWS
from tests.unit.constants import REGION, PROFILE


@pytest.fixture
def session(mocker):
    return mocker.patch('formica.aws.Session')


def test_session_needs_to_be_set(session):
    AWS._AWS__session = None
    with pytest.raises(AttributeError):
        AWS.current_session()


def test_AWS_constructor_cant_be_called(session):
    with pytest.raises(Exception):
        AWS()


def test_AWS_is_singleton(session):
    AWS.initialize()
    AWS.current_session()
    AWS.current_session()
    session.assert_called_once()


def test_init_without_parameters(session):
    AWS.initialize()
    session.assert_called_with()


def test_init_with_region(session):
    AWS.initialize(region=REGION)
    session.assert_called_with(region_name=REGION)


def test_init_with_profile(session):
    AWS.initialize(profile=PROFILE)
    session.assert_called_with(profile_name=PROFILE)


def test_init_with_profile_and_region(session):
    AWS.initialize(profile=PROFILE, region=REGION)
    session.assert_called_with(profile_name=PROFILE, region_name=REGION)
