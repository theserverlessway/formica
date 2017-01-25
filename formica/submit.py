import botocore
import click

from formica.loader import Loader


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
        click.echo('Change set submitted, waiting until creation ...')
        waiter = self.client.get_waiter('change_set_create_complete')
        waiter.wait(ChangeSetName=self.change_set_name, StackName=self.stack)
        click.echo('Change set created successfully')
        change_set = self.client.describe_change_set(StackName=self.stack, ChangeSetName=self.change_set_name)
        click.echo(change_set['Changes'])

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
