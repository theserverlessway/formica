#!/usr/bin/env python

import boto3
import botocore

import click

from . import template

client = boto3.client('cloudformation')

resource = boto3.resource('cloudformation')

@click.group()
def main():
    pass

@main.command()
def inspect():
    template.load()
    print(template.template.to_json())

@main.command()
@click.option('--stack', help='The stack you want to create.')
def create(stack):
    try:
        print('Creating the Cloudformation stack.')
        stack = client.describe_stacks(StackName=stack)
        click.echo('Stack was already created')
        return
    except botocore.exceptions.ClientError as e:
        template.load()
        stack = client.create_stack(
            StackName= stack,
            TemplateBody= template.template.to_json())
        waiter = client.get_waiter('stack_create_complete')
        waiter.wait(StackName= stack['StackId'])
        print('Stack Created')

@main.command()
@click.option('--stack', help='The stack you want to deploy to.')
def deploy(stack):
    template.load()
    try:
        print('Updating Stack')
        print(template.template.to_json())
        client.update_stack(StackName= stack, TemplateBody= template.template.to_json())
        client.get_waiter('stack_update_complete').wait(StackName= stack)
        print("Stack Update Finished")
    except Exception as e:
        print(e)
