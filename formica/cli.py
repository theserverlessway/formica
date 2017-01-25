#!/usr/bin/env python

import logging

import click

from .loader import Loader


def aws_options(f):
    f = click.option('--region', help='The stack you want to create.')(f)
    f = click.option('--profile', help='The stack you want to create.')(f)
    return f


def stack(message):
    return click.option('--stack', help=message)


@click.group()
@click.version_option()
@click.option('--debug/--no-debug', help='Enable debugging output')
def main(debug):
    logging.basicConfig(level=(logging.DEBUG if debug else logging.WARNING))


@main.command()
def inspect():
    loader = Loader()
    loader.load()
    click.echo(loader.template())


@main.command()
@stack('The stack you want to create.')
def create(stack):
    pass


@main.command()
@stack('The stack to submit your changes to.')
def submit(stack):
    pass


@main.command()
@stack('The stack you want to deploy to.')
def deploy(stack):
    loader.load()
    try:
        print('Updating Stack')
        print(loader.template.to_json())
        client.update_stack(StackName=stack,
                            TemplateBody=loader.template.to_json())
        client.get_waiter('stack_update_complete').wait(StackName=stack)
        print("Stack Update Finished")
    except Exception as e:
        print(e)
