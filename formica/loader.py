import glob
import json
import os
import sys

import logging
import yaml
from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateSyntaxError, TemplateNotFound
import arrow

from .exceptions import FormicaArgumentException

from . import yaml_tags
# To silence pyflakes warning of unused import
assert yaml_tags

logger = logging.getLogger(__name__)

FILE_TYPES = ['yml', 'yaml', 'json']

RESOURCES_KEY = "Resources"
MODULE_KEY = "From"

try:
    basestring
except NameError:
    basestring = str

ALLOWED_ATTRIBUTES = {
    "AWSTemplateFormatVersion": basestring,
    "Description": [basestring, str],
    "Metadata": dict,
    "Parameters": dict,
    "Mappings": dict,
    "Conditions": dict,
    "Transform": [str, basestring, list],
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
    return variable or '{"Ref": "AWS::NoValue"}'


class Loader(object):
    def __init__(self, path='.', filename='*', variables=None):
        if variables is None:
            variables = {}
        self.cftemplate = {}
        self.path = path
        self.filename = filename
        self.env = Environment(loader=FileSystemLoader('./', followlinks=True))
        self.env.filters.update({
            'code_escape': code_escape,
            'mandatory': mandatory,
            'resource': resource,
            'novalue': novalue
        })
        self.variables = variables

    def include_file(self, filename, **args):
        source = self.render(filename, **args)
        return code_escape(source)

    def load_file(self, filename, **args):
        with open(filename) as f:
            return f.read()

    def render(self, filename, **args):
        template_path = os.path.normpath("{}/{}".format(self.path, filename))
        template = self.env.get_template(template_path)
        arguments = dict(code=self.include_file,
                         file=self.load_file,
                         now=arrow.now,
                         utcnow=arrow.utcnow,
                         **args)
        return template.render(**arguments)

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
                new_type = type(new)
                types = ALLOWED_ATTRIBUTES.get(key)
                if type(types) != list:
                    types = [types]
                if key in ALLOWED_ATTRIBUTES.keys() and new_type in types:
                    if new_type == basestring or new_type == str or new_type == list:
                        self.cftemplate[key] = new
                    elif new_type == dict:
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
            files.extend(glob.glob('{}/{}.template.{}'.format(self.path, self.filename, file_type)))

        if not files:
            logger.info("Could not find any template files in {}".format(self.path))
            sys.exit(1)

        for file in files:
            try:
                result = str(self.render(os.path.basename(file), **self.variables))
                template = yaml.load(result)
            except TemplateNotFound as e:
                logger.info('File not found' + ': ' + e.message)
                logger.info(
                    'In: "' + file + '"')
                sys.exit(1)
            except TemplateSyntaxError as e:
                logger.info(e.__class__.__name__ + ': ' + e.message)
                logger.info(
                    'File: "' + (e.filename or file) + '", line ' + str(e.lineno))
                sys.exit(1)
            except FormicaArgumentException as e:
                logger.info(e.__class__.__name__ + ': ' + e.args[0])
                logger.info(
                    'For Template: "' + file + '"')
                logger.info('If you use it as a template make sure you\'re setting all necessary vars')
                sys.exit(1)
            except yaml.YAMLError as e:
                logger.info(e.__str__())
                logger.info('Following is the Yaml document formica is trying to load:')
                logger.info('---------------------------------------------------------------------------')
                logger.info(result)
                logger.info('---------------------------------------------------------------------------')
                sys.exit(1)
            self.merge(template, file)
