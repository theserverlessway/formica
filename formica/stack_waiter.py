import sys
import time

import logging
from texttable import Texttable

EVENT_TABLE_HEADERS = ['Timestamp', 'Status', 'Type', 'Logical ID', 'Status reason']

TABLE_COLUMN_SIZE = [28, 24, 30, 30, 50]

SUCCESSFUL_STATES = ['CREATE_COMPLETE', 'UPDATE_COMPLETE', 'DELETE_COMPLETE']
FAILED_STATES = ['CREATE_FAILED', 'DELETE_FAILED', 'ROLLBACK_FAILED', 'ROLLBACK_COMPLETE', 'UPDATE_FAILED',
                 'UPDATE_ROLLBACK_FAILED', 'UPDATE_ROLLBACK_COMPLETE']


logger = logging.getLogger(__name__)


class StackWaiter:
    def __init__(self, stack, client):
        self.stack = stack
        self.client = client

    def wait(self, last_event):
        self.print_header()
        finished = False
        while not finished:
            time.sleep(5)
            stack_events = self.client.describe_stack_events(StackName=self.stack)['StackEvents']
            index = next((i for i, v in enumerate(stack_events) if v['EventId'] == last_event))
            last_event = stack_events[0]['EventId']
            new_events = stack_events[0:index]
            if new_events:
                self.print_events(new_events)
            stack_status = self.client.describe_stacks(StackName=self.stack)['Stacks'][0]['StackStatus']
            if stack_status in SUCCESSFUL_STATES:
                finished = True
            elif stack_status in FAILED_STATES:
                sys.exit(1)

    def __create_table(self):
        table = Texttable()
        table.set_cols_width(TABLE_COLUMN_SIZE)
        return table

    def print_header(self):
        table = self.__create_table()
        table.add_rows([EVENT_TABLE_HEADERS])
        table.set_deco(Texttable.BORDER | Texttable.VLINES)
        logger.info(table.draw())

    def print_events(self, events):
        table = self.__create_table()
        table.set_deco(0)
        for event in reversed(events):
            table.add_row([
                event['Timestamp'].strftime('%Y-%m-%d %H:%M:%S %Z%z'),
                event['ResourceStatus'],
                event['ResourceType'],
                event['LogicalResourceId'],
                event.get('ResourceStatusReason', '')
            ])
        logger.info(table.draw())
