import logging
import sys
import time

from .aws import AWS
from .helper import collect_vars, main_account_id, aws_accounts, aws_regions
from .diff import compare_stack_set
from texttable import Texttable

logger = logging.getLogger(__name__)

STACK_SET_SUCCESS_STATES = ['SUCCEEDED']
STACK_SET_RUNNING_STATES = ['RUNNING', 'STOPPING']


def requires_stack_set(function):
    def validate_stack_set(args):
        if not args.stack_set:
            logger.error('You need to set the stack set either with --stack-set(-s) or '
                         'in a config file set with --config-file(-c)')
            sys.exit(1)
        else:
            function(args)

    return validate_stack_set


def requires_accounts_regions(function):
    def validate_stack_set(args):
        if (args.accounts or args.all_accounts or args.all_subaccounts or args.main_account) and (
                args.regions or args.all_regions or args.excluded_regions):
            function(args)
        else:
            logger.error('You need to set the regions and accounts you want to update.')
            sys.exit(1)

    return validate_stack_set


def ack(message):
    return input('{}: [y/yes]: '.format(message)).lower() in ['y', 'yes']


@requires_stack_set
def update_stack_set(args):
    compare_stack_set(stack=args.stack_set, vars=collect_vars(args), parameters=args.parameters, tags=args.tags,
                      main_account_parameter=args.main_account_parameter)
    if args.yes or ack('Do you want to update the StackSet with above changes'):
        __manage_stack_set(args=args, create=False)
    else:
        logger.info('StackSet Update canceled')
        sys.exit(1)


@requires_stack_set
def create_stack_set(args):
    __manage_stack_set(args=args, create=True)


@requires_stack_set
def remove_stack_set(args):
    client = AWS.current_session().client('cloudformation')
    client.delete_stack_set(StackSetName=args.stack_set)
    logger.info('Removed StackSet with name {}'.format(args.stack_set))


def accounts_table(accounts_map):
    table = Texttable(max_width=150)
    table.set_cols_dtype(['t', 't'])
    table.add_rows([['Account', 'Regions']])

    for account, regions in accounts_map.items():
        table.add_row([account, ', '.join(regions)])

    logger.info(table.draw() + "\n")


@requires_stack_set
@requires_accounts_regions
def add_stack_set_instances(args):
    client = AWS.current_session().client('cloudformation')
    paginator = client.get_paginator('list_stack_instances')
    deployed = [{'Account': stack['Account'], 'Region': stack['Region']} for page in
                paginator.paginate(StackSetName=args.stack_set) for stack in page['Summaries']]

    expected_instances = [{'Account': account, 'Region': region} for account in accounts(args) for region in
                          regions(args)]

    new_instances = [i for i in expected_instances if i not in deployed]
    if new_instances:
        new_accounts = sorted(list(set([i['Account'] for i in new_instances])))
        new_regions = sorted(list(set([i['Region'] for i in new_instances])))

        account_to_region = {a: set([i['Region'] for i in new_instances if i['Account'] == a]) for a in new_accounts}

        if len(new_instances) == len(expected_instances) or len(new_accounts) == 1 or len(new_regions) == 1:
            targets = [(new_accounts, new_regions)]
        else:
            targets = [([i['Account'] for i in new_instances if i['Region'] == region], [region]) for region in
                       new_regions]

        logger.info('Adding new StackSet Instances:')
        accounts_table(account_to_region)
        if args.yes or ack('Do you want to add these StackSet Instances:'):
            for target in targets:
                preferences = operation_preferences(args)
                result = client.create_stack_instances(StackSetName=args.stack_set,
                                                       Accounts=target[0],
                                                       Regions=target[1],
                                                       **preferences)
                wait_for_stack_set_operation(args.stack_set, result['OperationId'])
        else:
            logger.info('Adding StackSet Instances canceled')
            sys.exit(1)
    else:
        logger.info('All StackSet Instances are deployed')


@requires_stack_set
@requires_accounts_regions
def remove_stack_set_instances(args):
    client = AWS.current_session().client('cloudformation')
    preferences = operation_preferences(args)
    acc = accounts(args)
    reg = regions(args)
    logger.info('Removing StackSet Instances for StackSet {}'.format(args.stack_set))
    accounts_table({a: reg for a in acc})
    if args.yes or ack('Do you want to remove these StackSet Instances'):
        result = client.delete_stack_instances(StackSetName=args.stack_set,
                                               Accounts=acc,
                                               Regions=reg,
                                               RetainStacks=args.retain,
                                               **preferences)
        wait_for_stack_set_operation(args.stack_set, result['OperationId'])
    else:
        logger.info('Removing StackSet Instances canceled')
        sys.exit(1)


@requires_stack_set
def diff_stack_set(args):
    from .diff import compare_stack_set
    compare_stack_set(stack=args.stack_set, vars=collect_vars(args), parameters=args.parameters, tags=args.tags,
                      main_account_parameter=args.main_account_parameter)


def wait_for_stack_set_operation(stack_set_name, operation_id):
    logger.info('Waiting for StackSet Operation {} on StackSet {} to finish'.format(operation_id, stack_set_name))
    client = AWS.current_session().client('cloudformation')
    finished = False
    status = ''
    while not finished:
        time.sleep(5)
        status = client.describe_stack_set_operation(StackSetName=stack_set_name, OperationId=operation_id)[
            'StackSetOperation']['Status']
        if status in STACK_SET_RUNNING_STATES:
            sys.stdout.write('.')
            sys.stdout.flush()
        else:
            finished = True
            logger.info('')

    logger.info('StackSet Operation finished with Status: {}'.format(status))
    if status not in STACK_SET_SUCCESS_STATES:
        sys.exit(1)


def accounts(args):
    if (type(args) != dict):
        args = vars(args)
    if args.get('accounts'):
        return [str(a) for a in args['accounts']]
    elif args['main_account']:
        return [main_account_id()]
    elif args['all_subaccounts']:
        return [a['Id'] for a in aws_accounts()['AWSSubAccounts']]
    elif args['all_accounts']:
        return [a['Id'] for a in aws_accounts()['AWSAccounts']]


def regions(args):
    if vars(args).get('regions'):
        return vars(args)['regions']
    elif args.excluded_regions:
        excluded_regions = [r for r in aws_regions()['AWSRegions'] if r not in args.excluded_regions]
        return excluded_regions
    elif args.all_regions:
        return aws_regions()['AWSRegions']


def __manage_stack_set(args, create):
    from .loader import Loader
    client = AWS.current_session().client('cloudformation')
    params = args.parameters or {}
    account_regions = {}
    if not create:
        account_regions = dict(
            accounts=accounts(args),
            regions=regions(args)
        )

    params = parameters(parameters=params,
                        tags=args.tags,
                        capabilities=args.capabilities,
                        execution_role_name=args.execution_role_name,
                        administration_role_arn=args.administration_role_arn,
                        **account_regions)

    if not create:
        preferences = operation_preferences(args)
        # Necessary for python 2.7 as it can't merge dicts with **
        params.update(preferences)

    loader = Loader(variables=collect_vars(args), main_account_parameter=args.main_account_parameter)
    loader.load()
    template = loader.template(indent=None)

    if create:
        result = client.create_stack_set(
            StackSetName=args.stack_set,
            TemplateBody=template,
            **params
        )
        logger.info('StackSet {} created'.format(args.stack_set))
    else:
        result = client.update_stack_set(
            StackSetName=args.stack_set,
            TemplateBody=template,
            **params
        )
        wait_for_stack_set_operation(args.stack_set, result['OperationId'])


def parameters(parameters, tags, capabilities, execution_role_name, administration_role_arn, accounts=[], regions=[]):
    optional_arguments = {}
    if parameters:
        optional_arguments['Parameters'] = [
            {'ParameterKey': key, 'ParameterValue': str(value), 'UsePreviousValue': False} for (key, value)
            in parameters.items()]
    if tags:
        optional_arguments['Tags'] = [{'Key': key, 'Value': str(value)} for (key, value) in
                                      tags.items()]
    if capabilities:
        optional_arguments['Capabilities'] = capabilities
    if accounts:
        optional_arguments['Accounts'] = accounts
    if regions:
        optional_arguments['Regions'] = regions
    if execution_role_name:
        optional_arguments['ExecutionRoleName'] = execution_role_name
    if administration_role_arn:
        optional_arguments['AdministrationRoleARN'] = administration_role_arn
    return optional_arguments


def operation_preferences(args):
    operation_preferences = {}
    varargs = vars(args)
    region_order = varargs.get('region_order')
    max_concurrent_count = varargs.get('max_concurrent_count')
    max_concurrent_percentage = varargs.get('max_concurrent_percentage')
    failure_tolerance_count = varargs.get('failure_tolerance_count')
    failure_tolerance_percentage = varargs.get('failure_tolerance_percentage')

    if region_order:
        operation_preferences['RegionOrder'] = region_order
    if max_concurrent_count:
        operation_preferences['MaxConcurrentCount'] = max_concurrent_count
    if max_concurrent_percentage:
        operation_preferences['MaxConcurrentPercentage'] = max_concurrent_percentage
    if failure_tolerance_count:
        operation_preferences['FailureToleranceCount'] = failure_tolerance_count
    if failure_tolerance_percentage:
        operation_preferences['FailureTolerancePercentage'] = failure_tolerance_percentage
    if operation_preferences:
        return {'OperationPreferences': operation_preferences}
    else:
        return {}
