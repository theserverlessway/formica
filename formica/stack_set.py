from formica.aws import AWS
from .loader import Loader
import logging

logger = logging.getLogger(__name__)


def update_stack_set(args):
    __manage_stack_set(args=args, create=False)


def create_stack_set(args):
    __manage_stack_set(args=args, create=True)


def remove_stack_set(args):
    client = AWS.current_session().client('cloudformation')
    client.delete_stack_set(StackSetName=args.stack_set)
    logger.info('Removed StackSet with name {}'.format(args.stack_set))


def add_stack_set_instances(args):
    client = AWS.current_session().client('cloudformation')
    client.create_stack_instances(StackSetName=args.stack_set,
                                  Accounts=args.accounts,
                                  Regions=args.regions)
    logger.info('Added StackSet Instances for StackSet {}'.format(args.stack_set))


def remove_stack_set_instances(args):
    client = AWS.current_session().client('cloudformation')
    client.delete_stack_instances(StackSetName=args.stack_set,
                                  Accounts=args.accounts,
                                  Regions=args.regions,
                                  RetainStacks=args.retain)
    logger.info('Removed StackSet Instances for StackSet {}'.format(args.stack_set))


def __manage_stack_set(args, create):
    client = AWS.current_session().client('cloudformation')
    params = parameters(parameters=args.parameters,
                        tags=args.tags,
                        capabilities=args.capabilities,
                        accounts=vars(args).get('accounts'),
                        regions=vars(args).get('regions'),
                        execution_role_name=args.execution_role_name,
                        administration_role_arn=args.administration_role_arn)
    loader = Loader(variables=args.vars)
    loader.load()
    if create:
        result = client.create_stack_set(
            StackSetName=args.stack_set,
            TemplateBody=loader.template(),
            ** params
        )
        logger.info('StackSet {} created'.format(args.stack_set))
    else:
        result = client.update_stack_set(
            StackSetName=args.stack_set,
            TemplateBody=loader.template(),
            ** params
        )
        logger.info('StackSet {} updated in Operation {}'.format(args.stack_set, result['OperationId']))


def parameters(parameters, tags, capabilities, accounts, regions, execution_role_name, administration_role_arn):
    optional_arguments = {}
    if parameters:
        optional_arguments['Parameters'] = [
            {'ParameterKey': key, 'ParameterValue': value, 'UsePreviousValue': False} for (key, value)
            in parameters.items()]
    if tags:
        optional_arguments['Tags'] = [{'Key': key, 'Value': value, } for (key, value) in
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
