import sys
from functools import wraps

import click
from botocore.exceptions import ProfileNotFound, NoCredentialsError, NoRegionError, ClientError

from formica.aws import AWS


def name(*names):
    name = ''.join(map(lambda name: name.title(), names))
    name = ''.join(e for e in name if e.isalnum())
    return name


def aws_exceptions(function):
    @wraps(function)
    def wrapped(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except (ProfileNotFound, NoCredentialsError, NoRegionError) as e:
            click.echo('Please make sure your credentials, regions and profiles are properly set:')
            click.echo(e)
            sys.exit(1)
        except ClientError as e:
            if e.response['Error']['Code'] == 'ValidationError':
                click.echo(e.response['Error']['Message'])
                sys.exit(1)
            else:
                click.echo(e)
                sys.exit(2)

    return wrapped


def session_wrapper(function):
    @wraps(function)
    def wrap(*args, **kwargs):
        AWS.initialize(kwargs['region'], kwargs['profile'])
        del (kwargs['region'])
        del (kwargs['profile'])
        return function(*args, **kwargs)

    return wrap
