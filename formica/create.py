import botocore
import click

from formica.loader import Loader


class Create:
    def __init__(self, stack_name, aws_session):
        self.stack_name = stack_name
        self.aws_session = aws_session

    def create(self):
        client = self.aws_session.client_for('cloudformation')
        try:
            click.echo('Creating the Cloudformation stack.')
            client.describe_stacks(StackName=self.stack_name)
            click.echo('Stack was already created')
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'ValidationError':
                loader = Loader()
                loader.load()
                client.create_stack(
                    StackName=self.stack_name,
                    TemplateBody=loader.template())
                waiter = client.get_waiter('stack_create_complete')
                waiter.wait(StackName=self.stack_name)
                print('Stack Created')
            else:
                raise e
