from troposphere import AWSHelperFn, Template

import glob
import os
import string
import inspect
import pkgutil
import importlib
import troposphere
from . import helper

template = Template()

TROPOSPHERE_PATH = os.path.dirname(troposphere.__file__)

DISALLOWED_MODULES = [
    'openstack',
    'template_generator',
    'utils',
    'helpers',
    'validators',
    'dynamodb2']

TROPOSPHERE_MODULE_NAMES = [
    name for _, name, _ in pkgutil.iter_modules([TROPOSPHERE_PATH])
        if name not in DISALLOWED_MODULES]

TROPOSPHERE_MODULES = {
    name: importlib.import_module(f'troposphere.{name}') for name in TROPOSPHERE_MODULE_NAMES}

CLOUDFORMATION_FUNCTIONS = {x.__name__: x for x in AWSHelperFn.__subclasses__()}

def load(path=os.getcwd(), part='*', variables={}):
    formica_commands = {
        'resource': lambda resource: template.add_resource(resource),
        'mapping': lambda name, value: template.add_mapping(name, values),
        'module': module,
        'name': helper.name}
    toload = f'{path}/{part}.fc'
    for file in glob.glob(toload):
        with open(file) as f:
            code = compile(f.read(), file, 'exec')
            exec(code, {**formica_commands, **CLOUDFORMATION_FUNCTIONS, **TROPOSPHERE_MODULES, **variables}, )

def module(module_name, part='*', **variables):
    filepath = os.path.dirname(inspect.stack()[1].filename)
    load(filepath.rstrip('/') + '/' + module_name.strip('/'), part, variables)
