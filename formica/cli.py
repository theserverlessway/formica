#!/usr/bin/env python

import functools
import argparse
import argcomplete
import sys
import logging


from . import CHANGE_SET_FORMAT, __version__
from .aws import AWS


from . import stack_set


STACK_HEADERS = ['Name', 'Created At', 'Updated At', 'Status']
RESOURCE_HEADERS = ['Logical ID', 'Physical ID', 'Type', 'Status']

logger = logging.getLogger(__name__)

CONFIG_FILE_ARGUMENTS = {
    'stack': str,
    'stack_set': str,
    'tags': dict,
    'parameters': dict,
    'role_arn': str,
    'role_name': str,
    'region': str,
    'profile': str,
    'capabilities': list,
    'vars': dict,
    'administration_role_arn': str,
    'administration_role_name': str,
    'execution_role_name': str,
    'main_account': bool,
    'accounts': list,
    'regions': list,
    'all_accounts': bool,
    'all_subaccounts': bool,
    'all_regions': bool,
    'region_order': list,
    'failure_tolerance_count': int,
    'failure_tolerance_percentage': int,
    'max_concurrent_count': int,
    'max_concurrent_percentage': int
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
                                       help='Available commands', dest='command')
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

    # Stack Set Configuration
    stack_set_parser(subparsers)

    # Autocomplete
    argcomplete.autocomplete(parser)

    # Argument Parsing
    args = parser.parse_args(cli_args)

    if vars(args).get('config_file'):
        load_config_files(args, args.config_file)

    args_dict = vars(args)

    from botocore.exceptions import NoRegionError, ClientError, EndpointConnectionError
    from botocore.exceptions import ProfileNotFound, NoCredentialsError

    try:
        # Initialise the AWS Profile and Region
        AWS.initialize(args_dict.get('region'), args_dict.get('profile'))

        convert_role_name_to_arn(args)

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


def convert_role_name_to_arn(args):
    args_dict = vars(args)
    sts = AWS.current_session().client('sts')
    if args_dict.get('role_name') and not args_dict.get('role_arn'):
        account_id = sts.get_caller_identity()['Account']
        args.role_arn = 'arn:aws:iam::{}:role/{}'.format(account_id, args.role_name)
    if args_dict.get('administration_role_name') and not args_dict.get('administration_role_arn'):
        account_id = sts.get_caller_identity()['Account']
        args.administration_role_arn = 'arn:aws:iam::{}:role/{}'.format(account_id, args.administration_role_name)


def stack_set_parser(parser):
    # Stack Set Commang Arguments

    stack_set_parser = parser.add_parser('stack-set', description='Manage Stack Sets')
    stack_set_subparsers = stack_set_parser.add_subparsers(title='stack-set',
                                                           help='Available commands', dest='command')

    # Stack-Set
    create_parser = stack_set_subparsers.add_parser('create', description='Create a Stack Set')
    add_aws_arguments(create_parser)
    add_stack_set_argument(create_parser)
    add_stack_parameters_argument(create_parser)
    add_stack_set_main_account_parameter(create_parser)
    add_stack_tags_argument(create_parser)
    add_capabilities_argument(create_parser)
    add_config_file_argument(create_parser)
    add_stack_variables_argument(create_parser)
    add_stack_set_role_argument(create_parser)
    create_parser.set_defaults(func=stack_set.create_stack_set)

    update_parser = stack_set_subparsers.add_parser('update', description='Update a Stack Set')
    add_aws_arguments(update_parser)
    add_stack_set_argument(update_parser)
    add_stack_parameters_argument(update_parser)
    add_stack_set_main_account_parameter(update_parser)
    add_stack_tags_argument(update_parser)
    add_capabilities_argument(update_parser)
    add_config_file_argument(update_parser)
    add_stack_variables_argument(update_parser)
    add_stack_set_role_argument(update_parser)
    add_stack_set_instance_arguments(update_parser)
    add_stack_set_main_auto_regions_accounts(update_parser)
    add_stack_set_operation_preferences(update_parser)
    update_parser.set_defaults(func=stack_set.update_stack_set)

    remove_parser = stack_set_subparsers.add_parser('remove', description='Remove a Stack Set')
    add_aws_arguments(remove_parser)
    add_stack_set_argument(remove_parser)
    add_config_file_argument(remove_parser)
    remove_parser.set_defaults(func=stack_set.remove_stack_set)

    add_instances_parser = stack_set_subparsers.add_parser('add-instances',
                                                           description='Add Stack Set Instances')
    add_aws_arguments(add_instances_parser)
    add_stack_set_argument(add_instances_parser)
    add_stack_set_instance_arguments(add_instances_parser)
    add_config_file_argument(add_instances_parser)
    add_stack_set_main_auto_regions_accounts(add_instances_parser)
    add_stack_set_operation_preferences(add_instances_parser)
    add_instances_parser.set_defaults(func=stack_set.add_stack_set_instances)

    remove_instances_parser = stack_set_subparsers.add_parser('remove-instances',
                                                              description='Remove Stack Set Instances')
    add_aws_arguments(remove_instances_parser)
    add_stack_set_argument(remove_instances_parser)
    add_stack_set_instance_arguments(remove_instances_parser)
    add_stack_set_instance_retain_argument(remove_instances_parser)
    add_config_file_argument(remove_instances_parser)
    add_stack_set_main_auto_regions_accounts(remove_instances_parser)
    add_stack_set_operation_preferences(remove_instances_parser)
    remove_instances_parser.set_defaults(func=stack_set.remove_stack_set_instances)

    diff_parser = stack_set_subparsers.add_parser('diff',
                                                  description='Diff the StackSet template to the local template')
    add_aws_arguments(diff_parser)
    add_stack_set_argument(diff_parser)
    add_config_file_argument(diff_parser)
    add_stack_variables_argument(diff_parser)
    diff_parser.set_defaults(func=stack_set.diff_stack_set)


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


def add_stack_set_argument(parser):
    parser.add_argument('--stack-set', '-s', help='The Stack Set to use', metavar='STACK-Set')


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
    parser.add_argument('--role-name', help='Set a role name that will be translated to the ARN')


def add_stack_set_role_argument(parser):
    parser.add_argument('--administration-role-arn', help='The Administration Role to create the StackSet')
    parser.add_argument('--administration-role-name',
                        help='The Administration Role name that will be translated to the ARN')
    parser.add_argument('--execution-role-name', help='The Execution role name to use for the CloudFormation Stack')


def add_stack_set_instance_arguments(parser):
    parser.add_argument('--accounts', nargs='+', help='The Accounts for this operation')
    parser.add_argument('--regions', nargs='+', help='The Regions for this operation')


def add_stack_set_instance_retain_argument(parser):
    parser.add_argument('--retain', help='Retain stacks', action='store_true', default=False)


def add_stack_set_main_account_parameter(parser):
    parser.add_argument('--main-account', help='Set MainAccount Parameter', action='store_true', default=False)


def add_stack_set_main_auto_regions_accounts(parser):
    parser.add_argument('--all-accounts', help='Use All Accounts of this Org', action='store_true', default=False)
    parser.add_argument('--all-subaccounts', help='Use Only Subaccounts of this Org',
                        action='store_true', default=False)
    parser.add_argument('--all-regions', help='Use all Regions', action='store_true', default=False)


def add_stack_set_operation_preferences(parser):
    parser.add_argument('--region-order', help='Order in which to deploy to regions', nargs='+', default=[])
    failure_tolerance = parser.add_mutually_exclusive_group()
    failure_tolerance.add_argument('--failure-tolerance-count',
                                   help='Number of Stacks to fail before failing operation', type=int)
    failure_tolerance.add_argument('--failure-tolerance-percentage',
                                   help='Percentage of Stacks to fail before failing operation', type=int)
    max_concurrent = parser.add_mutually_exclusive_group()
    max_concurrent.add_argument('--max-concurrent-count',
                                help='Max Number of concurrent accounts to deploy to', type=int)
    max_concurrent.add_argument('--max-concurrent-percentage',
                                help='Max Percentage of concurrent accounts to deploy to', type=int)


def add_config_file_argument(parser):
    parser.add_argument('--config-file', '-c',
                        type=argparse.FileType('r'),
                        help='Set the config files to use',
                        nargs='+')


def add_s3_upload_argument(parser):
    parser.add_argument('--s3', help='Upload template to S3 before deployment', action='store_true')


def template(args):
    from .loader import Loader
    import yaml
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
    from texttable import Texttable
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
    from .diff import compare
    client = AWS.current_session().client('cloudformation')

    template = client.get_template(
        StackName=args.stack,
    )
    compare(template['TemplateBody'], args.vars)


@requires_stack
def describe(args):
    from .change_set import ChangeSet
    client = AWS.current_session().client('cloudformation')
    change_set = ChangeSet(stack=args.stack, client=client)
    change_set.describe()


@requires_stack
def resources(args):
    from texttable import Texttable
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
    from .change_set import ChangeSet
    from .loader import Loader
    client = AWS.current_session().client('cloudformation')
    loader = Loader(variables=args.vars)
    loader.load()

    change_set = ChangeSet(stack=args.stack, client=client)
    change_set.create(template=loader.template(indent=None), change_set_type='UPDATE', parameters=args.parameters,
                      tags=args.tags, capabilities=args.capabilities, role_arn=args.role_arn, s3=args.s3)
    change_set.describe()


@requires_stack
def deploy(args):
    from .stack_waiter import StackWaiter
    client = AWS.current_session().client('cloudformation')
    last_event = client.describe_stack_events(StackName=args.stack)['StackEvents'][0]['EventId']
    client.execute_change_set(ChangeSetName=(CHANGE_SET_FORMAT.format(stack=args.stack)), StackName=args.stack)
    StackWaiter(args.stack, client).wait(last_event)


@requires_stack
def remove(args):
    from .stack_waiter import StackWaiter
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
    from .change_set import ChangeSet
    from .loader import Loader
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
    import yaml
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
            if isinstance(value, config_type):
                if config_type == dict and args_dict.get(key):
                    merged = value
                    merged.update(args_dict[key])
                    args_dict[key] = merged
                else:
                    if not args_dict.get(key):
                        args_dict[key] = value
            else:
                logger.error('Config file parameter {} needs to be of type {}'.format(key, config_type.__name__))
                sys.exit(2)
        else:
            logger.error('Config file parameter {} is not supported'.format(key))
            sys.exit(2)
