import collections
import re
import yaml
import logging
from deepdiff import DeepDiff
from formica.aws import AWS
from texttable import Texttable

from formica.loader import Loader

logger = logging.getLogger(__name__)

try:
    basestring
except NameError:
    basestring = str


class Change():
    def __init__(self, path, before, after, type):
        self.path = path
        self.before = before
        self.after = after
        self.type = type


def convert(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert, data.items()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert, data))
    else:
        return data


def compare_stack(stack, vars=None, parameters={}, tags={}):
    client = AWS.current_session().client('cloudformation')
    template = client.get_template(
        StackName=stack,
    )['TemplateBody']

    stack = client.describe_stacks(
        StackName=stack,
    )['Stacks'][0]
    __compare(template, stack, vars, parameters, tags)


def compare_stack_set(stack, vars=None, parameters={}, tags={}, main_account_parameter=False):
    client = AWS.current_session().client('cloudformation')

    stack_set = client.describe_stack_set(
        StackSetName=stack,
    )['StackSet']
    __compare(stack_set['TemplateBody'], stack_set, vars, parameters, tags, main_account_parameter)


def __compare(template, stack, vars=None, parameters={}, tags={}, main_account_parameter=False):
    current_parameters = {p['ParameterKey']: p['ParameterValue'] for p in (stack.get('Parameters', []))}
    parameters = {key: str(value) for key, value in parameters.items()}
    tags = {key: str(value) for key, value in tags.items()}
    current_tags = {p['Key']: p['Value'] for p in (stack.get('Tags', []))}

    loader = Loader(variables=vars, main_account_parameter=main_account_parameter)
    loader.load()
    deployed_template = convert(template)
    template_parameters = {
        key: str(value['Default']).lower() if type(value['Default']) == bool else str(value['Default'])
        for key, value in (loader.template_dictionary().get('Parameters', {})).items() if 'Default' in value
    }

    template_parameters.update(parameters)
    if isinstance(deployed_template, str):
        deployed_template = yaml.load(deployed_template)

    __generate_table('Parameters', current_parameters, template_parameters)
    __generate_table('Tags', current_tags, tags)
    __generate_table('Template', deployed_template, convert(loader.template_dictionary()))


def __generate_table(header, current, new):
    changes = DeepDiff(current, new, ignore_order=False,
                       report_repetition=True,
                       verbose_level=2, view='tree')
    table = Texttable(max_width=200)
    table.set_cols_dtype(['t', 't', 't', 't'])
    table.add_rows([['Path', 'From', 'To', 'Change Type']])
    print_diff = False
    processed_changes = __collect_changes(changes)
    for change in processed_changes:
        print_diff = True
        path = re.findall('\\[\'?([\\w-]+)\'?\\]', change.path)
        table.add_row(
            [
                ' > '.join(path),
                change.before,
                change.after,
                change.type.title().replace('_', ' ')
            ]
        )
    logger.info(header + ' Diff:')
    if print_diff:
        logger.info(table.draw() + "\n")
    else:
        logger.info('No Changes found' + "\n")


def __collect_changes(changes):
    results = []
    for key, value in changes.items():
        for change in list(value):
            results.append(Change(path=change.path(), before=change.t1, after=change.t2, type=key))
    return sorted(results, key=lambda x: x.path)
