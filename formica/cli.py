#!/usr/bin/env python

import yaml
import functools
import argparse
import sys
import logging
from texttable import Texttable

from formica import CHANGE_SET_FORMAT, __version__
from formica.aws import AWS
from formica.change_set import ChangeSet
from formica.diff import Diff
from formica.stack_waiter import StackWaiter
from .loader import Loader
from botocore.exceptions import ProfileNotFound, NoCredentialsError, NoRegionError, ClientError, EndpointConnectionError


STACK_HEADERS = ['Name', 'Created At', 'Updated At', 'Status']
RESOURCE_HEADERS = ['Logical ID', 'Physical ID', 'Type', 'Status']

logger = logging.getLogger(__name__)

CONFIG_FILE_ARGUMENTS = {
    'stack': str,
    'tags': dict,
    'parameters': dict,
    'role_arn': str,
    'region': str,
    'profile': str,
    'capabilities': list,
    'vars': dict,
}


class SplitEqualsAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values:
            parameters = {}
            try:
                for string in values:
                    key, value = string.split('=', 2)
                    parameters[key] = value
                    setattr(namespace, self.dest, parameters)
            except ValueError:
                raise argparse.ArgumentError(self, '%r needs to be in format KEY=VALUE' % string)


def formica():
    main(sys.argv[1:])


def main(cli_args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version='{}'.format(__version__))
    subparsers = parser.add_subparsers(title='commands',
                                       help='Command to use', dest='command')
    subparsers.required = True

    # Template Command Arguments
    template_parser = subparsers.add_parser('template', description='Print the current template')
    add_config_file_argument(template_parser)
    add_stack_variables_argument(template_parser)
    template_parser.add_argument('-y', '--yaml', help="print output as yaml", action="store_true")
    template_parser.set_defaults(func=template)

    # Stacks Command Arguments
    stacks_parser = subparsers.add_parser('stacks', description='List all stacks')
    add_aws_arguments(stacks_parser)
    add_config_file_argument(stacks_parser)
    stacks_parser.set_defaults(func=stacks)

    # New Command Arguments
    new_parser = subparsers.add_parser('new', description='Create a change set for a new stack')
    add_aws_arguments(new_parser)
    add_stack_argument(new_parser)
    add_stack_parameters_argument(new_parser)
    add_stack_tags_argument(new_parser)
    add_capabilities_argument(new_parser)
    add_role_arn_argument(new_parser)
    add_config_file_argument(new_parser)
    add_stack_variables_argument(new_parser)
    add_s3_upload_argument(new_parser)
    new_parser.set_defaults(func=new)

    # Change Command Arguments
    change_parser = subparsers.add_parser('change', description='Create a change set for an existing stack')
    add_aws_arguments(change_parser)
    add_stack_argument(change_parser)
    add_stack_parameters_argument(change_parser)
    add_stack_tags_argument(change_parser)
    add_capabilities_argument(change_parser)
    add_role_arn_argument(change_parser)
    add_config_file_argument(change_parser)
    add_stack_variables_argument(change_parser)
    add_s3_upload_argument(change_parser)
    change_parser.set_defaults(func=change)

    # Deploy Command Arguments
    deploy_parser = subparsers.add_parser('deploy', description='Deploy the latest change set for a stack')
    add_aws_arguments(deploy_parser)
    add_stack_argument(deploy_parser)
    add_config_file_argument(deploy_parser)
    deploy_parser.set_defaults(func=deploy)

    # Describe Command Arguments
    describe_parser = subparsers.add_parser('describe', description='Describe the latest change-set of the stack')
    add_aws_arguments(describe_parser)
    add_stack_argument(describe_parser)
    add_config_file_argument(describe_parser)
    describe_parser.set_defaults(func=describe)

    # Diff Command Arguments
    diff_parser = subparsers.add_parser('diff', description='Print a diff between local and deployed stack')
    add_aws_arguments(diff_parser)
    add_stack_argument(diff_parser)
    add_config_file_argument(diff_parser)
    add_stack_variables_argument(diff_parser)
    diff_parser.set_defaults(func=diff)

    # Resources Command Arguments
    resources_parser = subparsers.add_parser('resources', description='List all resources of a stack')
    add_aws_arguments(resources_parser)
    add_stack_argument(resources_parser)
    add_config_file_argument(resources_parser)
    resources_parser.set_defaults(func=resources)

    # Remove Command Arguments
    remove_parser = subparsers.add_parser('remove', description='Remove the configured stack')
    add_aws_arguments(remove_parser)
    add_stack_argument(remove_parser)
    add_role_arn_argument(remove_parser)
    add_config_file_argument(remove_parser)
    remove_parser.set_defaults(func=remove)

    # Argument Parsing
    args = parser.parse_args(cli_args)
    args_dict = vars(args)

    if args_dict.get('config_file'):
        load_config_files(args, args.config_file)

    try:
        # Initialise the AWS Profile and Region
        AWS.initialize(args_dict.get('region'), args_dict.get('profile'))

        # Execute Function
        if args_dict.get('func'):
            args.func(args)
        else:
            parser.print_usage()
    except (ProfileNotFound, NoCredentialsError, NoRegionError, EndpointConnectionError) as e:
        logger.info('Please make sure your credentials, regions and profiles are properly set:')
        logger.info(e)
        sys.exit(1)
    except ClientError as e:
        if e.response['Error']['Code'] == 'ValidationError':
            logger.info(e.response['Error']['Message'])
            sys.exit(1)
        else:
            logger.info(e)
            sys.exit(2)


def requires_stack(function):
    def validate_stack(args):
        if not args.stack:
            logger.error('You need to set the stack either with --stack(-s) or '
                         'in a config file set with --config-file(-c)')
            sys.exit(1)
        else:
            function(args)
    return validate_stack


def add_aws_arguments(parser):
    parser.add_argument('--region', help='The AWS region to use', metavar='REGION')
    parser.add_argument('--profile', help='The AWS profile to use', metavar='PROFILE')


def add_stack_argument(parser):
    parser.add_argument('--stack', '-s', help='The Stack to use', metavar='STACK')


def add_stack_parameters_argument(parser):
    parser.add_argument('--parameters', help='Add one or multiple stack parameters',
                        nargs='+', action=SplitEqualsAction, metavar='KEY=Value')


def add_stack_variables_argument(parser):
    parser.add_argument('--vars', help='Add one or multiple Jinja2 variables',
                        nargs='+', action=SplitEqualsAction, metavar='KEY=Value')


def add_stack_tags_argument(parser):
    parser.add_argument('--tags', help='Add one or multiple stack tags', nargs='+',
                        action=SplitEqualsAction, metavar='KEY=Value')


def add_capabilities_argument(parser):
    parser.add_argument('--capabilities', help='Set one or multiple stack capabilities',
                        metavar='Cap1 Cap2', nargs='+')


def add_role_arn_argument(parser):
    parser.add_argument('--role-arn', help='Set a separate role ARN to pass to the stack')


def add_config_file_argument(parser):
    parser.add_argument('--config-file', '-c',
                        type=argparse.FileType('r'),
                        help='Set the config files to use',
                        nargs='+')


def add_s3_upload_argument(parser):
    parser.add_argument('--s3', help='Upload template to S3 before deployment', action='store_true')


def template(args):
    loader = Loader(variables=args.vars)
    loader.load()
    if args.yaml:
        logger.info(
            loader.template(
                dumper=functools.partial(yaml.safe_dump, default_flow_style=False)
            ).strip()  # strip trailing newline to avoid blank line in output
        )
    else:
        logger.info(loader.template(indent=4, separators=(',', ': ')))


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

    logger.info("Current Stacks:\n" + table.draw() + "\n")


@requires_stack
def diff(args):
    Diff(AWS.current_session()).run(args.stack, args.vars)


@requires_stack
def describe(args):
    client = AWS.current_session().client('cloudformation')
    change_set = ChangeSet(stack=args.stack, client=client)
    change_set.describe()


@requires_stack
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

    logger.info(table.draw() + "\n")


@requires_stack
def change(args):
    client = AWS.current_session().client('cloudformation')
    loader = Loader(variables=args.vars)
    loader.load()

    change_set = ChangeSet(stack=args.stack, client=client)
    change_set.create(template=loader.template(indent=None), change_set_type='UPDATE', parameters=args.parameters,
                      tags=args.tags, capabilities=args.capabilities, role_arn=args.role_arn, s3=args.s3)
    change_set.describe()


@requires_stack
def deploy(args):
    client = AWS.current_session().client('cloudformation')
    last_event = client.describe_stack_events(StackName=args.stack)['StackEvents'][0]['EventId']
    client.execute_change_set(ChangeSetName=(CHANGE_SET_FORMAT.format(stack=args.stack)), StackName=args.stack)
    StackWaiter(args.stack, client).wait(last_event)


@requires_stack
def remove(args):
    client = AWS.current_session().client('cloudformation')
    stack_id = client.describe_stacks(StackName=args.stack)['Stacks'][0]['StackId']
    logger.info('Removing Stack and waiting for it to be removed, ...')
    last_event = client.describe_stack_events(StackName=args.stack)['StackEvents'][0]['EventId']
    if args.role_arn:
        client.delete_stack(StackName=args.stack, RoleARN=args.role_arn)
    else:
        client.delete_stack(StackName=args.stack)
    StackWaiter(stack_id, client).wait(last_event)


@requires_stack
def new(args):
    client = AWS.current_session().client('cloudformation')
    loader = Loader(variables=args.vars)
    loader.load()
    logger.info('Creating change set for new stack, ...')
    change_set = ChangeSet(stack=args.stack, client=client)
    change_set.create(template=loader.template(indent=None), change_set_type='CREATE', parameters=args.parameters,
                      tags=args.tags, capabilities=args.capabilities, role_arn=args.role_arn, s3=args.s3)
    change_set.describe()
    logger.info('Change set created, please deploy')


def load_config_files(args, config_files):
    config_file_args = dict()
    for config_file in config_files:
        try:
            file_items = yaml.load(config_file.read())
            for key, value in file_items.items():
                if key in config_file_args and isinstance(value, dict):
                    subdict = config_file_args[key]
                    for subkey, subvalue in value.items():
                        subdict[subkey] = subvalue
                else:
                    config_file_args[key] = value
        except yaml.YAMLError as e:
            logger.error(e.__str__())
            sys.exit(1)
    args_dict = vars(args)
    for key, value in config_file_args.items():
        key = key.replace('-', '_')
        if key in CONFIG_FILE_ARGUMENTS.keys():
            config_type = CONFIG_FILE_ARGUMENTS[key]
            if not args_dict.get(key) and value:
                if isinstance(value, config_type):
                    args_dict[key] = value
                else:
                    logger.error('Config file parameter {} needs to be of type {}'.format(key, config_type.__name__))
                    sys.exit(2)
        else:
            logger.error('Config file parameter {} is not supported'.format(key))
            sys.exit(2)
