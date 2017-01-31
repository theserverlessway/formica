#!/usr/bin/env python

import logging

import click
from texttable import Texttable

from formica import CHANGE_SET_FORMAT
from formica.change_set import ChangeSet
from formica.helper import aws_exceptions, session_wrapper
from .loader import Loader

STACK_HEADERS = ['Name', 'Created At', 'Updated At', 'Status']


def aws_options(f):
    f = session_wrapper(f)
    f = click.option('--region', help='The stack you want to create.')(f)
    f = click.option('--profile', help='The stack you want to create.')(f)
    return f


def stack(message):
    return click.option('--stack', help=message, required=True)


@click.group()
@click.version_option()
@click.option('--debug/--no-debug', help='Enable debugging output')
def main(debug):
    logging.basicConfig(level=(logging.DEBUG if debug else logging.WARNING))


@main.command()
def show():
    """Print the current template"""
    loader = Loader()
    loader.load()
    click.echo(loader.template())


@main.command()
@stack('The stack you want to create.')
@aws_exceptions
@aws_options
def new(stack, profile, region, session):
    """Create a change set for a new stack"""
    client = session.client_for('cloudformation')
    loader = Loader()
    loader.load()
    click.echo('Creating change set for new stack, ...')
    change_set = ChangeSet(stack=stack, client=client, template=loader.template(),
                           type='CREATE')
    change_set.create()
    click.echo('Change set created, please deploy.')


@main.command()
@stack('The stack to submit your changes to.')
@aws_exceptions
@aws_options
def change(stack, profile, region, session):
    """Create a change set for an existing stack"""
    client = session.client_for('cloudformation')
    loader = Loader()
    loader.load()

    change_set = ChangeSet(stack=stack, client=client, template=loader.template(),
                           type='UPDATE')
    change_set.create()


@main.command()
@stack('The stack you want to deploy to.')
@aws_exceptions
@aws_options
def deploy(stack, region, profile, session):
    """Deploy the latest change set for a stack"""
    client = session.client_for('cloudformation')
    click.echo('Executing Changeset')
    client.execute_change_set(ChangeSetName=(CHANGE_SET_FORMAT.format(stack=stack)), StackName=stack)
    waiter = client.get_waiter('stack_update_complete')
    waiter.wait(StackName=stack)
    click.echo('Deployment successful')


@main.command()
@aws_exceptions
@aws_options
def stacks(region, profile, session):
    """List all stacks"""
    client = session.client_for('cloudformation')
    stacks = client.describe_stacks()
    table = Texttable(max_width=150)
    print(stacks)
    table.add_row(STACK_HEADERS)

    for stack in stacks['Stacks']:
        table.add_row(
            [stack['StackName'],
             stack['CreationTime'],
             stack.get('LastUpdatedTime', ''),
             stack['StackStatus']
             ])

    click.echo("Current Stacks:\n" + table.draw() + "\n")


@main.command()
@stack('The stack you want to destroy.')
@aws_exceptions
@aws_options
def remove(stack, region, profile, session):
    """Remove the configured stack"""
    client = session.client_for('cloudformation')
    click.echo('Removing Stack and waiting for it to be removed, ...')
    client.delete_stack(StackName=stack)
    waiter = client.get_waiter('stack_delete_complete')
    waiter.wait(StackName=stack)
