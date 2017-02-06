import unittest
from unittest.mock import Mock, patch

from formica.stack_waiter import StackWaiter, EVENT_TABLE_HEADERS
from tests.constants import STACK, STACK_EVENTS


@patch('formica.stack_waiter.time')
class TestStackWaiter(unittest.TestCase):
    def setUp(self):
        self.cf_client_mock = Mock()
        self.stack_waiter = StackWaiter(STACK, self.cf_client_mock)

    def set_stack_status_returns(self, statuses):
        self.cf_client_mock.describe_stacks.side_effect = [{'Stacks': [{'StackStatus': status}]} for status in
                                                           statuses]

    def set_stack_events(self, events=1):
        self.stack_events = {'StackEvents': [{"EventId": str(num)} for num in range(events)]}
        self.cf_client_mock.describe_stack_events.return_value = self.stack_events

    @patch.object(StackWaiter, 'print_header')
    def test_prints_header(self, header, time):
        self.set_stack_status_returns(['CREATE_COMPLETE'])
        self.set_stack_events()
        self.stack_waiter.wait('0')
        header.assert_called()

    def test_waits_until_successful(self, time):
        self.set_stack_status_returns(['UPDATE_IN_PROGRESS', 'CREATE_COMPLETE'])
        self.set_stack_events()
        self.stack_waiter.wait('0')
        self.assertEqual(time.sleep.call_count, 2)
        time.sleep.assert_called_with(5)

    def test_waits_until_failed_and_raises(self, time):
        self.set_stack_status_returns(['UPDATE_IN_PROGRESS', 'CREATE_FAILED'])
        self.set_stack_events()
        with self.assertRaises(SystemExit, msg='1'):
            self.stack_waiter.wait('0')
        self.assertEqual(time.sleep.call_count, 2)

    @patch('formica.stack_waiter.click')
    def test_prints_new_events(self, click, time):
        self.set_stack_status_returns(['CREATE_COMPLETE'])
        self.cf_client_mock.describe_stack_events.return_value = STACK_EVENTS
        self.stack_waiter.wait('DeploymentBucket3-7c92066b-c2e7-427a-ab29-53b928925473')

        click.echo.assert_called()
        output = '\n'.join([call[1][0] for call in click.echo.mock_calls])
        to_search = []
        to_search.extend(EVENT_TABLE_HEADERS)
        to_search.extend(['UPDATE_COMPLETE', 'DELETE_COMPLETE'])
        to_search.extend(['AWS::S3::Bucket', 'AWS::CloudFormation::Stack'])
        to_search.extend(['2017-02-06 16:01:16', '2017-02-06 16:01:16', '2017-02-06 16:01:17'])
        to_search.extend(['DeploymentBucket14', 'DeploymentBucket18', 'teststack '])
        to_search.extend(['Resource creation Initiated'])
        for term in to_search:
            self.assertIn(term, output)

        old_events = ['DeploymentBucket3', 'DeploymentBucket15']
        for term in old_events:
            self.assertNotIn(term, output)
        self.assertNotIn('None', output)
