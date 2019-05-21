import sys

import pytest

from formica.aws import AWS
from tests.unit.constants import REGION, PROFILE


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
    if sys.version_info >= (3, 6):
        session.assert_called_once()
    else:
        assert session.call_count == 1


def test_init_without_parameters(session, botocore_session):
    AWS.initialize()
    session.assert_called_with(botocore_session=botocore_session())


def test_init_with_region(session, botocore_session):
    AWS.initialize(region=REGION)
    session.assert_called_with(botocore_session=botocore_session(), region_name=REGION)


def test_init_with_profile(session, botocore_session):
    AWS.initialize(profile=PROFILE)
    botocore_session.assert_called_with(profile=PROFILE)
    session.assert_called_with(botocore_session=botocore_session())


def test_init_with_profile_and_region(session, botocore_session):
    AWS.initialize(profile=PROFILE, region=REGION)
    botocore_session.assert_called_with(profile=PROFILE)
    session.assert_called_with(botocore_session=botocore_session(), region_name=REGION)
