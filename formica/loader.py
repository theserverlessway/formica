from troposphere import AWSHelperFn, Template

import glob
import os
import inspect
import pkgutil
import importlib
import troposphere
from . import helper

DISALLOWED_MODULES = [
    'openstack',
    'template_generator',
    'utils',
    'helpers',
    'validators',
    'dynamodb2']

TROPOSPHERE_PATH = os.path.dirname(troposphere.__file__)

TROPOSPHERE_MODULE_NAMES = [
    name for _, name, _ in pkgutil.iter_modules([TROPOSPHERE_PATH])
    if name not in DISALLOWED_MODULES]

TROPOSPHERE_MODULES = {name: importlib.import_module(
    f'troposphere.{name}') for name in TROPOSPHERE_MODULE_NAMES}

CLOUDFORMATION_FUNCTIONS = {
    x.__name__: x for x in AWSHelperFn.__subclasses__()}


class Loader():
    def __init__(self):
        self.cftemplate = Template()

    def template(self):
        return self.cftemplate.to_json()

    def module(self, module_name, part='*', **variables):
        filepath = os.path.dirname(inspect.stack()[1].filename)
        self.load(
            filepath.rstrip('/') +
            '/' +
            module_name.strip('/'),
            part,
            variables)

    def load(self, path=os.getcwd(), part='*', variables={}):
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
            'module': self.module,
            'name': helper.name}
        toload = f'{path}/{part}.fc'
        for file in glob.glob(toload):
            with open(file) as f:
                code = compile(f.read(), file, 'exec')
                exec(code,
                     {**formica_commands,
                      **CLOUDFORMATION_FUNCTIONS,
                      **TROPOSPHERE_MODULES,
                      **variables},
                     )
