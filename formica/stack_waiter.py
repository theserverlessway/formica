import sys
import time
from datetime import datetime

import logging
from texttable import Texttable

EVENT_TABLE_HEADERS = ['Timestamp', 'Status', 'Type', 'Logical ID', 'Status reason']

TABLE_COLUMN_SIZE = [28, 24, 30, 30, 50]

SUCCESSFUL_STATES = ['CREATE_COMPLETE', 'UPDATE_COMPLETE', 'DELETE_COMPLETE']
FAILED_STATES = ['CREATE_FAILED', 'DELETE_FAILED', 'ROLLBACK_FAILED', 'ROLLBACK_COMPLETE', 'UPDATE_FAILED',
                 'UPDATE_ROLLBACK_FAILED', 'UPDATE_ROLLBACK_COMPLETE']

logger = logging.getLogger(__name__)

SLEEP_TIME = 5


class StackWaiter:
    def __init__(self, stack, client, timeout=0):
        self.stack = stack
        self.client = client
        self.timeout = timeout

    def wait(self, last_event):
        header_printed = False
        finished = False
        canceled = False
        start = datetime.now()
        while not finished:
            stack_events = self.client.describe_stack_events(StackName=self.stack)['StackEvents']
            index = next((i for i, v in enumerate(stack_events) if v['EventId'] == last_event))
            last_event = stack_events[0]['EventId']
            new_events = stack_events[0:index]
            if new_events:
                if not header_printed:
                    self.print_header()
                    header_printed = True
                self.print_events(new_events)
            stack_status = self.stack_status()
            if stack_status in SUCCESSFUL_STATES:
                finished = True
                logger.info("Stack Status Successful: {}".format(stack_status))
            elif stack_status in FAILED_STATES:
                logger.info("Stack Status Failed: {}".format(stack_status))
                sys.exit(1)
            elif not canceled and self.timeout > 0 and (datetime.now() - start).seconds > (self.timeout * 60):
                logger.info("Timeout of {} minute(s) reached. Canceling Update.".format(self.timeout))
                canceled = True
                self.client.cancel_update_stack(StackName=self.stack)
            else:
                time.sleep(SLEEP_TIME)

    def stack_status(self):
        return self.client.describe_stacks(StackName=self.stack)['Stacks'][0]['StackStatus']

    def __create_table(self):
        table = Texttable()
        table.set_cols_width(TABLE_COLUMN_SIZE)
        return table

    def print_header(self):
        if self.timeout > 0:
            logger.info('Timeout set to {} minute(s)'.format(self.timeout))
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
