import boto3
import botocore

class AWSSession:
    def __init__(self, region='', profile=''):
        params = {}
        if region: params['region_name'] = region
        if profile: params['profile_name'] = profile
        self.session = boto3.session.Session(**params)

    def client_for(self, service):
        return self.session.client(service)


