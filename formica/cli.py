#!/usr/bin/env python

import logging

import click
from texttable import Texttable

from formica import CHANGE_SET_FORMAT
from formica.aws import AWS
from formica.change_set import ChangeSet
from formica.helper import aws_exceptions, session_wrapper
from formica.stack_waiter import StackWaiter
from .loader import Loader

STACK_HEADERS = ['Name', 'Created At', 'Updated At', 'Status']
RESOURCE_HEADERS = ['Logical ID', 'Physical ID', 'Type', 'Status']


def aws_options(f):
    f = session_wrapper(f)
    f = click.option('--region', help='The AWS region to use.', metavar='REGION')(f)
    f = click.option('--profile', help='The AWS profile to use.', metavar='PROFILE')(f)
    return f


def equals_option(ctx, param, value):
    parameters = {}
    try:
        for param in value:
            key, value = param.split('=', 2)
            parameters[key] = value
        return parameters
    except ValueError:
        raise click.BadParameter('needs to be in format KEY=VALUE')


def csv_option(ctx, param, value):
    if value:
        return value.split(',')
    else:
        return value


def stack_parameters(f):
    return click.option('--parameter', help='Add a parameter. Repeat for multiple parameters',
                        multiple=True, callback=equals_option, metavar='KEY=Value')(f)


def stack_tags(f):
    return click.option('--tag', help='Add a stack tag. Repeat for multipe tags', multiple=True,
                        callback=equals_option, metavar='KEY=Value')(f)


def capabilities(f):
    return click.option('--capabilities', help='Set one or multiple stack capabilities', callback=csv_option,
                        metavar='Cap1,Cap2')(f)


def stack(message):
    return click.option('--stack', help=message, required=True, metavar='STACK',
                        envvar='FORMICA_STACK')


@click.group()
@click.version_option()
@click.option('--debug/--no-debug', help='Enable debugging output')
def main(debug):
    logging.basicConfig(level=(logging.DEBUG if debug else logging.WARNING))


@main.command()
def template():
    """Print the current template"""
    loader = Loader()
    loader.load()
    click.echo(loader.template())


@main.command()
@stack('The stack you want to create.')
@aws_exceptions
@aws_options
@stack_parameters
@stack_tags
@capabilities
def new(stack, parameter, tag, capabilities):
    """Create a change set for a new stack"""
    client = AWS.current_session().client('cloudformation')
    loader = Loader()
    loader.load()
    click.echo('Creating change set for new stack, ...')
    change_set = ChangeSet(stack=stack, client=client)
    change_set.create(template=loader.template(), change_set_type='CREATE', parameters=parameter, tags=tag,
                      capabilities=capabilities)
    change_set.describe()
    click.echo('Change set created, please deploy.')


@main.command()
@stack('The stack to submit your changes to.')
@aws_exceptions
@aws_options
@stack_parameters
@stack_tags
@capabilities
def change(stack, parameter, tag, capabilities):
    """Create a change set for an existing stack"""
    client = AWS.current_session().client('cloudformation')
    loader = Loader()
    loader.load()

    change_set = ChangeSet(stack=stack, client=client)
    change_set.create(template=loader.template(), change_set_type='UPDATE', parameters=parameter, tags=tag,
                      capabilities=capabilities)
    change_set.describe()


@main.command()
@stack('The stack you want to deploy to.')
@aws_exceptions
@aws_options
def deploy(stack):
    """Deploy the latest change set for a stack"""
    client = AWS.current_session().client('cloudformation')
    last_event = client.describe_stack_events(StackName=stack)['StackEvents'][0]['EventId']
    client.execute_change_set(ChangeSetName=(CHANGE_SET_FORMAT.format(stack=stack)), StackName=stack)
    StackWaiter(stack, client).wait(last_event)


@main.command()
@aws_exceptions
@aws_options
def stacks():
    """List all stacks"""
    client = AWS.current_session().client('cloudformation')
    stacks = client.describe_stacks()
    table = Texttable(max_width=150)
    table.add_rows([STACK_HEADERS])

    for stack in stacks['Stacks']:
        table.add_row(
            [stack['StackName'],
             stack['CreationTime'],
             stack.get('LastUpdatedTime', ''),
             stack['StackStatus']
             ])

    click.echo("Current Stacks:\n" + table.draw() + "\n")


@main.command()
@stack('The stack to describe')
@aws_exceptions
@aws_options
def describe(stack):
    """Describe the latest change set of the specified stack"""
    client = AWS.current_session().client('cloudformation')
    change_set = ChangeSet(stack=stack, client=client)
    change_set.describe()


@main.command()
@stack('The stack you want to remove.')
@aws_exceptions
@aws_options
def remove(stack):
    """Remove the configured stack"""
    client = AWS.current_session().client('cloudformation')
    stack_id = client.describe_stacks(StackName=stack)['Stacks'][0]['StackId']
    click.echo('Removing Stack and waiting for it to be removed, ...')
    last_event = client.describe_stack_events(StackName=stack)['StackEvents'][0]['EventId']
    client.delete_stack(StackName=stack)
    StackWaiter(stack_id, client).wait(last_event)


@main.command()
@stack('The stack see the resources for.')
@aws_exceptions
@aws_options
def resources(stack):
    """List all resources of a stack"""
    client = AWS.current_session().client('cloudformation')
    paginator = client.get_paginator('list_stack_resources').paginate(StackName=stack)

    table = Texttable(max_width=150)
    table.add_rows([RESOURCE_HEADERS])

    for page in paginator:
        for resource in page['StackResourceSummaries']:
            table.add_row(
                [resource['LogicalResourceId'],
                 resource['PhysicalResourceId'],
                 resource['ResourceType'],
                 resource['ResourceStatus']
                 ])

    click.echo(table.draw() + "\n")
