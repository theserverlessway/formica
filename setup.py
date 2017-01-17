"""Packaging settings."""


from codecs import open
from os.path import abspath, dirname, join
from subprocess import call

from setuptools import Command, find_packages, setup

from formica import __version__

this_dir = abspath(dirname(__file__))
with open(join(this_dir, 'README.md'), encoding='utf-8') as file:
    long_description = file.read()


class RunTests(Command):
    """Run all tests."""
    description = 'run tests'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Run all tests!"""
        errno = call(['py.test', '--cov=skele', '--cov-report=term-missing'])
        raise SystemExit(errno)


setup(
    name = 'formica',
    version = __version__,
    description = 'Simple Cloudformation stack management tooling.',
    long_description = long_description,
    url = 'https://github.com/cloudthropology/formica',
    author = 'Florian Motlik',
    author_email = 'florian.motlik@cloudthropology.com',
    license = 'MIT',
    classifiers = [
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: Public Domain',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords = 'cloudformation, aws, cloud',
    packages = find_packages(exclude=['docs', 'tests*']),
    install_requires = ['troposphere', 'boto3', 'click'],
    extras_require = {
        'test': ['coverage', 'pytest', 'pytest-cov'],
    },
    entry_points = {
        'console_scripts': [
            'formica=formica.cli:main',
        ],
    },
    cmdclass = {'test': RunTests},
)
