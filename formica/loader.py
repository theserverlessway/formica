import glob
import json
import os
import sys

import logging
import yaml
from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateSyntaxError

from .exceptions import FormicaArgumentException

from . import yaml_tags
# To silence pyflakes warning of unused import
assert yaml_tags

logger = logging.getLogger(__name__)

LINE_WHITESPACE_OFFSET = '  |'

FILE_TYPES = ['yml', 'yaml', 'json']

RESOURCES_KEY = "Resources"
MODULE_KEY = "From"

try:
    basestring
except NameError:
    basestring = str

ALLOWED_ATTRIBUTES = {
    "AWSTemplateFormatVersion": basestring,
    "Description": basestring,
    "Metadata": dict,
    "Parameters": dict,
    "Mappings": dict,
    "Conditions": dict,
    "Transform": dict,
    RESOURCES_KEY: dict,
    "Outputs": dict,
}


def code_escape(source):
    return source.replace('\n', '\\n').replace('"', '\\"')


def mandatory(a):
    from jinja2.runtime import Undefined
    if isinstance(a, Undefined) or a is None:
        raise FormicaArgumentException('Mandatory variable not set.')
    return a


def resource(name):
    if name is None:
        return ''
    else:
        return ''.join(e for e in name.title() if e.isalnum())


def novalue(variable):
    print('Var: {}'.format(variable))
    return variable or '{"Ref": "AWS::NoValue"}'


class Loader(object):
    def __init__(self, path='.', file='*', variables=None):
        if variables is None:
            variables = {}
        self.cftemplate = {}
        self.path = path
        self.file = file
        self.env = Environment(loader=FileSystemLoader(path, followlinks=True))
        self.env.filters.update({
            'code_escape': code_escape,
            'mandatory': mandatory,
            'resource': resource,
            'novalue': novalue
        })
        self.variables = variables

    def include_file(self, filename, **args):
        source = self.render(filename, **args)
        value = code_escape(source)
        return value

    def render(self, filename, **args):
        return self.env.get_template(filename).render(code=self.include_file, **args)

    def template(self, indent=4, sort_keys=True, separators=(',', ':'), dumper=None):
        if dumper is not None:
            return dumper(self.cftemplate)
        return json.dumps(self.cftemplate, indent=indent, sort_keys=sort_keys, separators=separators)

    def template_dictionary(self):
        return self.cftemplate

    def merge(self, template, file):
        if template:
            for key in template.keys():
                new = template[key]
                if key in ALLOWED_ATTRIBUTES.keys() and isinstance(new, ALLOWED_ATTRIBUTES[key]):
                    if ALLOWED_ATTRIBUTES[key] == basestring:
                        self.cftemplate[key] = new
                    elif ALLOWED_ATTRIBUTES[key] == dict:
                        for element_key, element_value in template[key].items():
                            if key == RESOURCES_KEY and isinstance(element_value, dict) and MODULE_KEY in element_value:
                                self.load_module(element_value[MODULE_KEY], element_key, element_value)
                            else:
                                self.cftemplate.setdefault(key, {})[element_key] = element_value
                else:
                    logger.info("Key '{}' in file {} is not valid".format(key, file))
                    sys.exit(1)
        else:
            logger.info('File {} is empty'.format(file))

    def load_module(self, module_path, element_key, element_value):
        module_path = self.path + '/' + '/'.join(module_path.lower().split('::'))
        file_name = "*"

        if not os.path.isdir(module_path):
            file_name = module_path.split('/')[-1]
            module_path = '/'.join(module_path.split('/')[:-1])

        properties = element_value.get('Properties', {})
        properties['module_name'] = element_key
        vars = self.merge_variables(properties)

        loader = Loader(module_path, file_name, vars)
        loader.load()
        self.merge(loader.template_dictionary(), file=file_name)

    def merge_variables(self, module_vars):
        merged_vars = {}
        for k, v in self.variables.items():
            merged_vars[k] = v
        for k, v in module_vars.items():
            merged_vars[k] = v
        return merged_vars

    def load(self):
        files = []

        for file_type in FILE_TYPES:
            files.extend(glob.glob('{}/{}.template.{}'.format(self.path, self.file, file_type)))

        if not files:
            logger.info("Could not find any template files in {}".format(self.path))
            sys.exit(1)

        for file in files:
            try:
                result = str(self.render(os.path.basename(file), **self.variables))
                template = yaml.load(result)
            except TemplateSyntaxError as e:
                logger.info(e.__class__.__name__ + ': ' + e.message)
                logger.info(
                    'File: "' + e.filename + '", line ' + str(e.lineno))
                logger.info(LINE_WHITESPACE_OFFSET + e.source.rstrip('\n'))
                sys.exit(1)
            except FormicaArgumentException as e:
                logger.info(e.__class__.__name__ + ': ' + e.args[0])
                logger.info(
                    'For Template: "' + file + '"')
                logger.info('If you use it as a template make sure you\'re setting all necessary vars')
                sys.exit(1)
            except yaml.YAMLError as e:
                logger.error(e.__str__())
                sys.exit(1)
            self.merge(template, file)
