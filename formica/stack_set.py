from formica.aws import AWS
import logging
import sys
import json

logger = logging.getLogger(__name__)


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
        if (args.accounts or args.all_accounts or args.all_subaccounts) and (args.regions or args.all_regions):
            function(args)
        else:
            logger.error('You need to set the regions and accounts you want to update.')
            sys.exit(1)
    return validate_stack_set


@requires_stack_set
def update_stack_set(args):
    __manage_stack_set(args=args, create=False)


@requires_stack_set
def create_stack_set(args):
    __manage_stack_set(args=args, create=True)


@requires_stack_set
def remove_stack_set(args):
    client = AWS.current_session().client('cloudformation')
    client.delete_stack_set(StackSetName=args.stack_set)
    logger.info('Removed StackSet with name {}'.format(args.stack_set))


@requires_stack_set
@requires_accounts_regions
def add_stack_set_instances(args):
    client = AWS.current_session().client('cloudformation')
    preferences = operation_preferences(args)
    client.create_stack_instances(StackSetName=args.stack_set,
                                  Accounts=accounts(args),
                                  Regions=regions(args),
                                  **preferences)
    logger.info('Added StackSet Instances for StackSet {}'.format(args.stack_set))


@requires_stack_set
@requires_accounts_regions
def remove_stack_set_instances(args):
    client = AWS.current_session().client('cloudformation')
    preferences = operation_preferences(args)
    client.delete_stack_instances(StackSetName=args.stack_set,
                                  Accounts=accounts(args),
                                  Regions=regions(args),
                                  RetainStacks=args.retain,
                                  **preferences)
    logger.info('Removed StackSet Instances for StackSet {}'.format(args.stack_set))


@requires_stack_set
def diff_stack_set(args):
    from .diff import compare
    client = AWS.current_session().client('cloudformation')
    stack_set = client.describe_stack_set(StackSetName=args.stack_set)
    compare(stack_set['StackSet']['TemplateBody'], args.vars)


def accounts(args):
    if (vars(args).get('accounts')):
        return vars(args)['accounts']
    elif(args.all_subaccounts):
        current_account = AWS.current_session().client('sts').get_caller_identity()['Account']
        return [a for a in all_accounts() if a != current_account]
    elif (args.all_accounts):
        return all_accounts()


def regions(args):
    if (vars(args).get('regions')):
        return vars(args)['regions']
    elif(args.all_regions):
        return all_regions()


def all_accounts():
    orgs = AWS.current_session().client('organizations')
    return [acc['Id'] for acc in orgs.list_accounts()['Accounts'] if acc['Status'] == 'ACTIVE']


def all_regions():
    ec2 = AWS.current_session().client('ec2')
    return [r['RegionName'] for r in ec2.describe_regions()['Regions']]


def __manage_stack_set(args, create):
    from .loader import Loader
    client = AWS.current_session().client('cloudformation')
    params = args.parameters or {}
    main_account = args.main_account
    if main_account:
        sts = AWS.current_session().client('sts')
        identity = sts.get_caller_identity()
        params['MainAccount'] = identity['Account']

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
                        ** account_regions)

    preferences = operation_preferences(args)
    # Necessary for python 2.7 as it can't merge dicts with **
    params.update(preferences)

    loader = Loader(variables=args.vars)
    loader.load()
    template = loader.template()
    if main_account:
        template = loader.template_dictionary()
        template['Parameters'] = template.get('Parameters') or {}
        template['Parameters']['MainAccount'] = {'Type': 'String'}
        template = json.dumps(template)

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
        logger.info('StackSet {} updated in Operation {}'.format(args.stack_set, result['OperationId']))


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
