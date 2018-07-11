import sys

import logging
import uuid
from formica.aws import AWS
from botocore.exceptions import ClientError, WaiterError
from texttable import Texttable

from formica import CHANGE_SET_FORMAT

CHANGE_SET_HEADER = ['Action', 'LogicalId', 'PhysicalId', 'Type', 'Replacement', 'Changed']

logger = logging.getLogger(__name__)


class ChangeSet:
    def __init__(self, stack, client):
        self.name = CHANGE_SET_FORMAT.format(stack=stack)
        self.stack = stack
        self.client = client

    def create(self, template, change_set_type, parameters=[], tags=[], capabilities=[], role_arn=None, s3=False):
        optional_arguments = {}
        if parameters:
            optional_arguments['Parameters'] = sorted([
                {'ParameterKey': key, 'ParameterValue': str(value), 'UsePreviousValue': False} for (key, value)
                in parameters.items()], key=lambda param: param['ParameterKey'])
        if tags:
            optional_arguments['Tags'] = [{'Key': key, 'Value': value, } for (key, value) in
                                          tags.items()]
        if role_arn:
            optional_arguments['RoleARN'] = role_arn
        if capabilities:
            optional_arguments['Capabilities'] = capabilities
        if change_set_type == 'UPDATE':
            self.remove_existing_changeset()

        try:
            if s3:
                session = AWS.current_session()
                s3_client = session.client('s3')
                bucket_name = 'formica-deploy-{}'.format(str(uuid.uuid4()).lower())
                bucket_path = '{}-template.json'.format(self.stack)
                logger.info('Creating Bucket: {}'.format(bucket_name))

                s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration=dict(LocationConstraint=session.region_name)
                )

                logger.info('Uploading to bucket: {}/{}'.format(bucket_name, bucket_path))
                s3_client.put_object(Bucket=bucket_name, Key=bucket_path, Body=template)
                template_url = 'https://{}.s3.amazonaws.com/{}'.format(bucket_name, bucket_path)
                optional_arguments['TemplateURL'] = template_url
            else:
                optional_arguments['TemplateBody'] = template

            self.client.create_change_set(StackName=self.stack,
                                          ChangeSetName=self.name, ChangeSetType=change_set_type,
                                          **optional_arguments)
            logger.info('Change set submitted, waiting for CloudFormation to calculate changes ...')
            waiter = self.client.get_waiter('change_set_create_complete')
            waiter.wait(ChangeSetName=self.name, StackName=self.stack)
            logger.info('Change set created successfully')
        except WaiterError as e:
            status_reason = e.last_response.get('StatusReason', '')
            logger.info(status_reason)
            if "didn't contain changes" not in status_reason:
                sys.exit(1)
        finally:
            if s3:
                logger.info('Deleting Object and Bucket: {}/{}'.format(bucket_name, bucket_path))
                s3_client.delete_object(Bucket=bucket_name, Key=bucket_path)
                s3_client.delete_bucket(Bucket=bucket_name)

    def describe(self):
        change_set = self.client.describe_change_set(StackName=self.stack, ChangeSetName=self.name)
        table = Texttable(max_width=150)

        logger.info("Deployment metadata:")
        parameters = ', '.join([parameter['ParameterKey'] + '=' + parameter['ParameterValue'] for parameter in
                                change_set.get('Parameters', [])])
        table.add_row(['Parameters', parameters])
        tags = [tag['Key'] + '=' + tag['Value'] for tag in
                change_set.get('Tags', [])]
        table.add_row(["Tags ", ', '.join(tags)])
        table.add_row(["Capabilities ", ', '.join(change_set.get('Capabilities', []))])
        logger.info(table.draw() + '\n')

        table.reset()
        table = Texttable(max_width=150)
        table.add_rows([CHANGE_SET_HEADER])

        def __change_detail(change):
            target_ = change['Target']
            attribute = target_['Attribute']
            if attribute == 'Properties':
                return target_['Name']
            else:
                return attribute

        for change in change_set['Changes']:
            resource_change = change['ResourceChange']
            table.add_row(
                [resource_change['Action'],
                 resource_change['LogicalResourceId'],
                 resource_change.get('PhysicalResourceId', ''),
                 resource_change['ResourceType'],
                 resource_change.get('Replacement', ''),
                 ', '.join(sorted(set([__change_detail(c) for c in resource_change['Details']])))
                 ])

        logger.info('Resource Changes:')
        logger.info(table.draw())

    def remove_existing_changeset(self):
        try:
            self.client.describe_change_set(StackName=self.stack,
                                            ChangeSetName=self.name)
            logger.info('Removing existing change set')
            self.client.delete_change_set(StackName=self.stack,
                                          ChangeSetName=self.name)
        except ClientError as e:
            if e.response['Error']['Code'] != 'ChangeSetNotFound':
                raise e
