import unittest
from mock import patch

from formica.aws import AWS
from tests.unit.constants import REGION, PROFILE


@patch('formica.aws.Session')
class AWSTest(unittest.TestCase):
    def test_session_needs_to_be_set(self, session):
        AWS._AWS__session = None
        with self.assertRaises(AttributeError):
            AWS.current_session()

    def test_AWS_is_singletong(self, session):
        AWS.initialize()
        AWS.current_session()
        AWS.current_session()
        session.assert_called_once()

    def test_init_without_parameters(self, session):
        AWS.initialize()
        session.assert_called_with()

    def test_init_with_region(self, session):
        AWS.initialize(region=REGION)
        session.assert_called_with(region_name=REGION)

    def test_init_with_profile(self, session):
        AWS.initialize(profile=PROFILE)
        session.assert_called_with(profile_name=PROFILE)

    def test_init_with_profile_and_region(self, session):
        AWS.initialize(profile=PROFILE, region=REGION)
        session.assert_called_with(profile_name=PROFILE, region_name=REGION)
