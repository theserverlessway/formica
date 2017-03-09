import glob
import json
import os
import sys

import click
import yaml
from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateSyntaxError

from .exceptions import FormicaArgumentException

LINE_WHITESPACE_OFFSET = '  |'

YAML_FILE_TYPES = ['yml', 'yaml']
JSON_FILE_TYPES = ['json']
FILE_TYPES = YAML_FILE_TYPES + JSON_FILE_TYPES

MODULES_ATTRIBUTE = 'Modules'

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
    "Resources": dict,
    "Outputs": dict,
    MODULES_ATTRIBUTE: list
}


def code_escape(source):
    return source.replace('\n', '\\n').replace('"', '\\"')


def mandatory(a):
    from jinja2.runtime import Undefined

    if isinstance(a, Undefined):
        raise FormicaArgumentException('Mandatory variable not set.')
    return a


def resource(name):
    name = ''.join(e for e in name.title() if e.isalnum())
    return name


class Loader(object):
    def __init__(self):
        self.cftemplate = {}

    def template(self, indent=4, sort_keys=True, separators=(',', ': ')):
        return json.dumps(self.cftemplate, indent=indent, sort_keys=sort_keys, separators=separators)

    def load(self, path='.', file='*', variables=None):
        if not variables:
            variables = {}
        env = Environment()
        env.filters['code_escape'] = code_escape
        env.filters['mandatory'] = mandatory
        env.filters['resource'] = resource
        env.loader = FileSystemLoader(path)

        def include_file(filename):
            source = env.loader.get_source(env, filename)[0]
            return code_escape(source)

        files = []

        for file_type in FILE_TYPES:
            files.extend(glob.glob('{}/{}.template.{}'.format(path, file, file_type)))

        if not files:
            click.echo("Could not find any template files in {}".format(path))
            sys.exit(1)

        for file in files:
            try:
                result = str(env.get_template(os.path.basename(file)).render(code=include_file, **variables))
            except TemplateSyntaxError as e:
                click.echo(e.__class__.__name__ + ': ' + e.message)
                click.echo(
                    'File: "' + e.filename + '", line ' + str(e.lineno))
                click.echo(LINE_WHITESPACE_OFFSET + e.source.rstrip('\n'))
                sys.exit(1)
            except FormicaArgumentException as e:
                click.echo(e.__class__.__name__ + ': ' + e.args[0])
                click.echo(
                    'For Template: "' + file + '"')
                click.echo('If you use it as a template make sure you\'re setting all necessary vars')
                sys.exit(1)
            if file.endswith(tuple(YAML_FILE_TYPES)):
                template = yaml.load(result)
            elif file.endswith(tuple(JSON_FILE_TYPES)):
                template = json.loads(result)
            else:
                template = {}

            for key in template.keys():
                new = template[key]
                if key in ALLOWED_ATTRIBUTES.keys() and isinstance(new, ALLOWED_ATTRIBUTES[key]):
                    if ALLOWED_ATTRIBUTES[key] == basestring:
                        self.cftemplate[key] = new
                    elif ALLOWED_ATTRIBUTES[key] == dict:
                        for element in template[key].keys():
                            self.cftemplate.setdefault(key, {})[element] = template[key][element]
                    elif key == MODULES_ATTRIBUTE and ALLOWED_ATTRIBUTES[key] == list:
                        for module in template[key]:
                            module_path = module.get('path')
                            file_name = module.get('template', '*')
                            vars = module.get('vars', {})
                            self.load(path + '/' + module_path, file_name, vars)
                    else:
                        click.echo("Key '{}' in file {} is not valid".format(key, file))
                        sys.exit(1)
                else:
                    click.echo("Key '{}' in file {} is not valid".format(key, file))
                    sys.exit(1)
