import boto3
import uuid
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

s3 = boto3.resource("s3")


class TemporaryS3Bucket(object):
    def __init__(self, bucket):
        self.bucket = bucket
        self.name = bucket.name

    def upload(self, body):
        file_name = str(uuid.uuid4()).lower()
        logger.info("Uploading to bucket: {}/{}".format(self.bucket.name, file_name))
        self.bucket.put_object(Key=file_name, Body=body)
        return file_name


@contextmanager
def temporary_bucket():
    bucket_name = "formica-deployment-{}".format(str(uuid.uuid4()).lower())
    bucket = s3.Bucket(bucket_name)
    try:
        bucket.create(CreateBucketConfiguration=dict(LocationConstraint=boto3.session.Session().region_name))
        yield TemporaryS3Bucket(bucket)
    finally:
        to_delete = [dict(Key=obj.key) for obj in bucket.objects.all()]
        if to_delete:
            logger.info("Deleting {} Objects Bucket: {}".format(len(to_delete), bucket.name))
            bucket.delete_objects(Delete=dict(Objects=to_delete))
        logger.info("Deleting Bucket: {}".format(bucket_name))
        bucket.delete()
