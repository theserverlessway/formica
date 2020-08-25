import boto3
import botocore
from botocore import credentials
import os


def initialize(region, profile):
    cli_cache = os.path.join(os.path.expanduser("~"), ".aws/cli/cache")

    session = botocore.session.Session(profile=profile)
    session.get_component("credential_provider").get_provider("assume-role").cache = credentials.JSONFileCache(
        cli_cache
    )
    boto3.setup_default_session(botocore_session=session, region_name=region, profile_name=profile)
