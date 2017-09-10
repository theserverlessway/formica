#!/usr/bin/env python

import yaml
import functools
import argparse
import sys
from texttable import Texttable

from formica import CHANGE_SET_FORMAT
from formica.aws import AWS
from formica.change_set import ChangeSet
from formica.diff import Diff
from formica.stack_waiter import StackWaiter
from .loader import Loader
from botocore.exceptions import ProfileNotFound, NoCredentialsError, NoRegionError, ClientError, EndpointConnectionError

STACK_HEADERS = ['Name', 'Created At', 'Updated At', 'Status']
RESOURCE_HEADERS = ['Logical ID', 'Physical ID', 'Type', 'Status']


def equals_option(string):
    parameters = {}
    try:
        key, value = string.split('=', 2)
        parameters[key] = value
        return parameters
    except ValueError:
        raise argparse.ArgumentTypeError('%r needs to be in format KEY=VALUE' % string)


def csv_option(string):
    string.split(',')


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='commands',
                                       help='--help')

    # Template Command Arguments
    template_parser = subparsers.add_parser('template', description='Print the current template')
    template_parser.add_argument('-y', '--yaml', help="print output as yaml", action="store_true")
    template_parser.set_defaults(func=template)

    # Stacks Command Arguments
    stacks_parser = subparsers.add_parser('stacks', description='List all stacks')
    add_aws_arguments(stacks_parser)
    stacks_parser.set_defaults(func=stacks)

    # New Command Arguments
    new_parser = subparsers.add_parser('new', description='Create a change set for a new stack')
    add_aws_arguments(new_parser)
    add_stack_argument(new_parser)
    add_stack_parameters_argument(new_parser)
    add_stack_tags_argument(new_parser)
    add_capabilities_argument(new_parser)
    new_parser.set_defaults(func=new)

    # Change Command Arguments
    change_parser = subparsers.add_parser('change', description='Create a change set for an existing stack')
    add_aws_arguments(change_parser)
    add_stack_argument(change_parser)
    add_stack_parameters_argument(change_parser)
    add_stack_tags_argument(change_parser)
    add_capabilities_argument(change_parser)
    change_parser.set_defaults(func=change)

    # Deploy Command Arguments
    deploy_parser = subparsers.add_parser('deploy', description='Deploy the latest change set for a stack')
    add_aws_arguments(deploy_parser)
    add_stack_argument(deploy_parser)
    deploy_parser.set_defaults(func=deploy)

    # Describe Command Arguments
    describe_parser = subparsers.add_parser('describe', description='Describe the latest change-set of the stack')
    add_aws_arguments(describe_parser)
    add_stack_argument(describe_parser)
    describe_parser.set_defaults(func=describe)

    # Diff Command Arguments
    diff_parser = subparsers.add_parser('diff', description='Print a diff between local and deployed stack')
    add_aws_arguments(diff_parser)
    add_stack_argument(diff_parser)
    diff_parser.set_defaults(func=diff)

    # Resources Command Arguments
    resources_parser = subparsers.add_parser('resources', description='List all resources of a stack')
    add_aws_arguments(resources_parser)
    add_stack_argument(resources_parser)
    resources_parser.set_defaults(func=resources)

    # Remove Command Arguments
    remove_parser = subparsers.add_parser('remove', description='Remove the configured stack')
    add_aws_arguments(remove_parser)
    add_stack_argument(remove_parser)
    remove_parser.set_defaults(func=remove)

    # Argument Parsing
    args = parser.parse_args()

    try:

        # Initialise the AWS Profile and Region
        args_dict = vars(args)
        AWS.initialize(args_dict.get('region'), args_dict.get('profile'))

        # Execute Function
        args.func(args)
    except (ProfileNotFound, NoCredentialsError, NoRegionError, EndpointConnectionError) as e:
        print('Please make sure your credentials, regions and profiles are properly set:')
        print(e)
        sys.exit(1)
    except ClientError as e:
        if e.response['Error']['Code'] == 'ValidationError':
            print(e.response['Error']['Message'])
            sys.exit(1)
        else:
            print(e)
            sys.exit(2)


def add_aws_arguments(parser):
    parser.add_argument('--region', help='The AWS region to use', metavar='REGION')
    parser.add_argument('--profile', help='The AWS profile to use', metavar='PROFILE')


def add_stack_argument(parser):
    parser.add_argument('-s', '--stack', help='The Stack to use', metavar='STACK', required=True)


def add_stack_parameters_argument(parser):
    parser.add_argument('--parameters', help='Add a parameter. Repeat for multiple parameters',
                        nargs='*', type=equals_option, metavar='KEY=Value', required=False)


def add_stack_tags_argument(parser):
    parser.add_argument('--tags', help='Add a stack tag. Repeat for multipe tags', nargs='*',
                        type=equals_option, metavar='KEY=Value', required=False)


def add_capabilities_argument(parser):
    parser.add_argument('--capabilities', help='Set one or multiple stack capabilities', type=csv_option,
                        metavar='Cap1,Cap2', required=False)


def template(args):
    loader = Loader()
    loader.load()
    if args.yaml:
        print(
            loader.template(
                dumper=functools.partial(yaml.safe_dump, default_flow_style=False)
            ).strip()  # strip trailing newline to avoid blank line in output
        )
    else:
        print(loader.template())


def stacks(args):
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

    print("Current Stacks:\n" + table.draw() + "\n")


def diff(args):
    Diff(AWS.current_session()).run(args.stack)


def describe(args):
    client = AWS.current_session().client('cloudformation')
    change_set = ChangeSet(stack=args.stack, client=client)
    change_set.describe()


def resources(args):
    client = AWS.current_session().client('cloudformation')
    paginator = client.get_paginator('list_stack_resources').paginate(StackName=args.stack)

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

    print(table.draw() + "\n")


def change(args):
    client = AWS.current_session().client('cloudformation')
    loader = Loader()
    loader.load()

    change_set = ChangeSet(stack=args.stack, client=client)
    change_set.create(template=loader.template(), change_set_type='UPDATE', parameters=args.parameters, tags=args.tags,
                      capabilities=args.capabilities)
    change_set.describe()


def deploy(args):
    client = AWS.current_session().client('cloudformation')
    last_event = client.describe_stack_events(StackName=args.stack)['StackEvents'][0]['EventId']
    client.execute_change_set(ChangeSetName=(CHANGE_SET_FORMAT.format(stack=args.stack)), StackName=args.stack)
    StackWaiter(args.stack, client).wait(last_event)


def remove(args):
    client = AWS.current_session().client('cloudformation')
    stack_id = client.describe_stacks(StackName=args.stack)['Stacks'][0]['StackId']
    print('Removing Stack and waiting for it to be removed, ...')
    last_event = client.describe_stack_events(StackName=args.stack)['StackEvents'][0]['EventId']
    client.delete_stack(StackName=args.stack)
    StackWaiter(stack_id, client).wait(last_event)


def new(args):
    client = AWS.current_session().client('cloudformation')
    loader = Loader()
    loader.load()
    print('Creating change set for new stack, ...')
    change_set = ChangeSet(stack=args.stack, client=client)
    change_set.create(template=loader.template(), change_set_type='CREATE', parameters=args.parameters, tags=args.tags,
                      capabilities=args.capabilities)
    change_set.describe()
    print('Change set created, please deploy')
