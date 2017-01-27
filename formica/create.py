import botocore
import click
import sys

from formica.loader import Loader


class Create:

    def __init__(self, stack_name, aws_session):
        self.stack_name = stack_name
        self.client = aws_session.client_for('cloudformation')

    def create(self):
        try:
            click.echo('Creating the Cloudformation stack.')
            self.client.describe_stacks(StackName=self.stack_name)
            click.echo('Stack already exists')
            sys.exit(1)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'ValidationError':
                loader = Loader()
                loader.load()
                self.client.create_stack(
                    StackName=self.stack_name,
                    TemplateBody=loader.template())
                waiter = self.client.get_waiter('stack_create_complete')
                waiter.wait(StackName=self.stack_name)
                print('Stack Created')
            else:
                raise e
