import datetime

from dateutil.tz import tzlocal

# noqa

REGION = 'us-east-1'
PROFILE = 'my-profile'
STACK = 'my-stack'
TEMPLATE = 'MYTEMPLATE'
CHANGESETNAME = f'{STACK}-change-set'
CHANGESETCHANGES = {'ChangeSetName': 'simpleteststack-change-set', 'ChangeSetId': 'arn:aws:cloudformation:eu-central-1:420759548424:changeSet/simpleteststack-change-set/979f29ac-40c9-4802-b496-0b3f38241bcd', 'StackId': 'arn:aws:cloudformation:eu-central-1:420759548424:stack/simpleteststack/a4f23770-e476-11e6-bfa4-500c44f62262', 'StackName': 'simpleteststack', 'CreationTime': datetime.datetime(2017, 1, 27, 9, 58, 3, 821000, tzinfo=tzlocal()), 'ExecutionStatus': 'AVAILABLE', 'Status': 'CREATE_COMPLETE', 'NotificationARNs': [], 'Capabilities': [], 'Changes': [{'Type': 'Resource', 'ResourceChange': {'Action': 'Remove', 'LogicalResourceId': 'DeploymentBucket', 'PhysicalResourceId': 'simpleteststack-deploymentbucket-1l7p61v6fxpry', 'ResourceType': 'AWS::S3::Bucket', 'Scope': [], 'Details': []}}, {'Type': 'Resource', 'ResourceChange': {'Action': 'Modify', 'LogicalResourceId': 'DeploymentBucket2', 'PhysicalResourceId': 'simpleteststack-deploymentbucket2-11ngaeftydtn7', 'ResourceType': 'AWS::S3::Bucket', 'Replacement': 'True', 'Scope': ['Properties', 'Tags'], 'Details': [{'Target': {'Attribute': 'Tags', 'RequiresRecreation': 'Never'}, 'Evaluation': 'Static', 'ChangeSource': 'DirectModification'}, {'Target': {'Attribute': 'Properties', 'Name': 'BucketName', 'RequiresRecreation': 'Always'}, 'Evaluation': 'Static', 'ChangeSource': 'DirectModification'}]}}, {'Type': 'Resource', 'ResourceChange': {'Action': 'Add', 'LogicalResourceId': 'DeploymentBucket3', 'ResourceType': 'AWS::S3::Bucket', 'Scope': [], 'Details': []}}], 'ResponseMetadata': {'RequestId': '2a95cc4f-e477-11e6-a696-5fdc4c9bb8c5', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '2a95cc4f-e477-11e6-a696-5fdc4c9bb8c5', 'content-type': 'text/xml', 'content-length': '2816', 'vary': 'Accept-Encoding', 'date': 'Fri, 27 Jan 2017 09:58:33 GMT'}, 'RetryAttempts': 0}}
