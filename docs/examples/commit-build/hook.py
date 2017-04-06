import logging
import os

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    client = boto3.client('codebuild')
    project = os.environ['CodeBuildProject']
    commit_id = event['Records'][0]['codecommit']['references'][0]['commit']
    logging.info('START_BUILD {}'.format({'project': project, 'commit_id': commit_id}))
    client.start_build(projectName=project, sourceVersion=commit_id)
