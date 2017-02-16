from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


from builtins import open
from builtins import range
from builtins import str

from future import standard_library

standard_library.install_aliases()
from builtins import object
import glob
import inspect
import os
import sys
import traceback

import click
from troposphere import Template

from formica.troposphere_attributes import TROPOSPHERE_MODULES, CLOUDFORMATION_FUNCTIONS, CLOUDFORMATION_DECLARATIONS
from . import helper

DISALLOWED_MODULES = [
    'openstack',
    'template_generator',
    'utils',
    'helpers',
    'validators',
    'dynamodb2']

CLOUDFORMATION_EXPORTS = {}
CLOUDFORMATION_EXPORTS.update({module.__name__.split('.')[-1]: module for module in TROPOSPHERE_MODULES})
CLOUDFORMATION_EXPORTS.update({function.__name__: function for function in CLOUDFORMATION_FUNCTIONS})
CLOUDFORMATION_EXPORTS.update({declaration.__name__: declaration for declaration in CLOUDFORMATION_DECLARATIONS})

LINE_WHITESPACE_OFFSET = '  |'


class Loader(object):
    def __init__(self):
        self.cftemplate = Template()

    def template(self):
        return self.cftemplate.to_json()

    def module(self, module_name, part='*', **variables):
        filepath = os.path.dirname(inspect.stack()[1][1])
        self.load(
            filepath.rstrip('/') +
            '/' +
            module_name.strip('/'),
            part,
            variables)

    def load(self, path='.', part='*', variables={}):
        formica_commands = {
            'resource':
                lambda resource: self.cftemplate.add_resource(resource),
            'mapping':
                lambda name, values: self.cftemplate.add_mapping(name, values),
            'description':
                lambda description:
                self.cftemplate.add_description(description),
            'metadata':
                lambda metadata: self.cftemplate.add_metadata(metadata),
            'condition':
                lambda name, condition:
                self.cftemplate.add_condition(name, condition),
            'parameter':
                lambda parameter:
                self.cftemplate.add_parameter(parameter),
            'output':
                lambda output:
                self.cftemplate.add_output(output),
            'module': self.module,
            'name': helper.name}
        toload = '{}/{}.fc'.format(path, part)
        available = {}
        available.update(formica_commands)
        available.update(CLOUDFORMATION_EXPORTS)
        available.update(variables)
        for file in glob.glob(toload):
            with open(file) as f:
                try:
                    code = compile(f.read(), file, 'exec')
                except SyntaxError as e:
                    click.echo(e.__class__.__name__ + ': ' + e.msg)
                    click.echo('File: "' + e.filename + '", line ' + str(e.lineno) + ', char ' + str(e.offset))
                    click.echo(LINE_WHITESPACE_OFFSET + e.text.rstrip('\n'))
                    click.echo(LINE_WHITESPACE_OFFSET + ''.join([' ' for x in range(e.offset - 1)]) + '^')
                    sys.exit(1)
                else:
                    try:

                        exec(code, available)
                    except Exception as e:
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        frame = traceback.extract_tb(exc_traceback)[1]
                        click.echo(e.__class__.__name__ + ': ' + str(e))
                        click.echo('File: "' + frame[0] + '", line ' + str(frame[1]))
                        click.echo(LINE_WHITESPACE_OFFSET + frame[3].rstrip('\n'))
                        sys.exit(1)
