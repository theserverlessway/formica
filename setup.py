"""Packaging settings."""

from os.path import abspath, dirname, join, isfile

from setuptools import setup

from formica import __version__

this_dir = abspath(dirname(__file__))
path = join(this_dir, 'build/README.rst')
long_description = ''
if isfile(path):
    with open(path) as file:
        long_description = file.read()

setup(
    name='formica-cli',
    python_requires=">=3.3",
    version=__version__,
    description='Simple AWS CloudFormation stack management tooling.',
    long_description=long_description,
    url='https://github.com/flomotlik/formica',
    author='Florian Motlik',
    author_email='flo@flomotlik.me',
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: Public Domain',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='cloudformation, aws, cloud',
    packages=['formica'],
    install_requires=['boto3>=1.8.0,<2.0.0', 'texttable>=1.2.0,<2.0.0', 'jinja2>=2.10,<3.0', 'pyyaml==3.13',
                      'deepdiff==3.3.0', 'arrow>=0.12.1,<1.0.0', 'argcomplete>=1.9.4'],
    entry_points={
        'console_scripts': [
            'formica=formica.cli:formica',
        ],
    }
)
