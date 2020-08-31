import boto3
from contextlib import contextmanager
import logging
import hashlib

logger = logging.getLogger(__name__)


class TemporaryS3Bucket(object):
    def __init__(self):
        self.objects = {}
        self.uploaded = False
        self.__sts = boto3.client("sts")
        self.s3_bucket = None

    def __digest(self, body):
        return str(hashlib.md5(body).hexdigest()).lower()

    def add(self, body):
        if type(body) == str:
            body = body.encode()
        object_name = self.__digest(body)
        self.objects[object_name] = body
        return object_name

    @property
    def name(self):
        body_hashes = "".join([key for key, _ in self.objects.items()]).encode()
        account_id = self.__sts.get_caller_identity()["Account"]
        name_digest_input = (account_id + self.__sts.meta.region_name + body_hashes.decode()).encode()
        body_hashes_hash = self.__digest(name_digest_input)
        return "formica-deploy-{}".format(body_hashes_hash)

    def upload(self):
        if not self.uploaded:
            s3 = boto3.resource("s3")
            self.uploaded = True
            self.s3_bucket = s3.Bucket(self.name)
            try:
                self.s3_bucket.create(CreateBucketConfiguration=dict(LocationConstraint=self.__sts.meta.region_name))
            except s3.meta.client.exceptions.BucketAlreadyOwnedByYou:
                logger.info("Artifact Bucket already exists")
            for name, body in self.objects.items():
                logger.info("Uploading to Bucket: {}/{}".format(self.name, name))
                self.s3_bucket.put_object(Key=name, Body=body)


@contextmanager
def temporary_bucket():
    temp_bucket = TemporaryS3Bucket()
    try:
        yield temp_bucket
    finally:
        if temp_bucket.uploaded:
            to_delete = [dict(Key=obj.key) for obj in temp_bucket.s3_bucket.objects.all()]
            if to_delete:
                logger.info("Deleting {} Objects from Bucket: {}".format(len(to_delete), temp_bucket.name))
                temp_bucket.s3_bucket.delete_objects(Delete=dict(Objects=to_delete))
            logger.info("Deleting Bucket: {}".format(temp_bucket.name))
            temp_bucket.s3_bucket.delete()
