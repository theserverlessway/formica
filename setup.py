"""Packaging settings."""

from codecs import open
from os.path import abspath, dirname, join

from setuptools import setup

from formica import __version__

this_dir = abspath(dirname(__file__))
with open(join(this_dir, 'README.md'), encoding='utf-8') as file:
    long_description = file.read()


setup(
    name='formica',
    version=__version__,
    description='Simple Cloudformation stack management tooling.',
    long_description=long_description,
    url='https://github.com/cloudthropology/formica',
    author='Florian Motlik',
    author_email='florian.motlik@cloudthropology.com',
    license='MIT',
    classifiers=[
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
    keywords='cloudformation, aws, cloud',
    packages=['formica'],
    install_requires=['troposphere==1.9.1', 'boto3==1.4.4', 'click==6.7'],
    entry_points={
        'console_scripts': [
            'formica=formica.cli:main',
        ],
    },
    test_suite="tests"
)
