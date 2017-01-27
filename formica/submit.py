import sys

import botocore
import click
from texttable import Texttable

from formica.loader import Loader

CHANGE_SET_HEADER = ['Action', 'LogicalId', 'PhysicalId', 'Type', 'Replacement', 'Changed']


class Submit:

    def __init__(self, stack, session):
        self.stack = stack
        self.change_set_name = f'{stack}-change-set'
        self.client = session.client_for('cloudformation')

    def submit(self):
        loader = Loader()
        loader.load()

        self.remove_existing_changeset()
        self.client.create_change_set(StackName=self.stack, TemplateBody=loader.template(),
                                      ChangeSetName=self.change_set_name)
        click.echo('ChangeSet submitted, waiting for CloudFormation to calculate changes ...')
        waiter = self.client.get_waiter('change_set_create_complete')
        try:
            waiter.wait(ChangeSetName=self.change_set_name, StackName=self.stack)
            click.echo('ChangeSet created successfully')
            change_set = self.client.describe_change_set(StackName=self.stack, ChangeSetName=self.change_set_name)
            self.print_changes(change_set)
        except botocore.exceptions.WaiterError as e:
            click.echo(e.last_response['StatusReason'])
            sys.exit(1)

    @staticmethod
    def print_changes(change_set):
        table = Texttable(max_width=150)

        table.add_row(CHANGE_SET_HEADER)

        def __change_detail(change):
            target_ = change['Target']
            attribute = target_['Attribute']
            if attribute == 'Properties':
                return target_['Name']
            else:
                return attribute

        for change in change_set['Changes']:
            resource_change = change['ResourceChange']
            table.add_row(
                [resource_change['Action'],
                 resource_change['LogicalResourceId'],
                 resource_change.get('PhysicalResourceId', ''),
                 resource_change['ResourceType'],
                 resource_change.get('Replacement', ''),
                 ', '.join([__change_detail(c) for c in resource_change['Details']])
                 ])

        click.echo("Changes to be deployed:\n" + table.draw() + "\n")

    def remove_existing_changeset(self):
        try:
            self.client.describe_change_set(StackName=self.stack,
                                            ChangeSetName=self.change_set_name)
            click.echo('Removing existing changeset')
            self.client.delete_change_set(StackName=self.stack,
                                          ChangeSetName=self.change_set_name)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] != 'ChangeSetNotFound':
                raise e
