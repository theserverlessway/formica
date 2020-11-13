import boto3
from contextlib import contextmanager
import logging
from hashlib import md5
from io import BytesIO

logger = logging.getLogger(__name__)

# Using MD5 for shorter string names as Sha256 is larger than allowed bucket name characters
HASH = md5
# Use Hash Blocksize to determine number of bytes read
BLOCKSIZE_MULTI = 512


class TemporaryS3Bucket(object):
    def __init__(self, seed):
        self.objects = {}
        self.uploaded = False
        self.__sts = boto3.client("sts")
        self.s3_bucket = None
        self.files = {}
        self.seed = seed

    def __digest(self, body):

        used_hash = HASH()
        for byte_block in iter(lambda: body.read(used_hash.block_size * BLOCKSIZE_MULTI), b""):
            used_hash.update(byte_block)
        return used_hash.hexdigest()

    def add(self, body):
        if type(body) == str:
            body = body.encode()
        with BytesIO(body) as b:
            object_name = self.__digest(b)
        self.objects[object_name] = body
        return object_name

    def add_file(self, file_name):
        with open(file_name, "rb") as f:
            object_name = self.__digest(f)
        self.files[object_name] = file_name
        return object_name

    @property
    def name(self):
        body_hashes = "".join(
            [key for key, _ in self.objects.items()] + [key for key, _ in self.files.items()]
        ).encode()
        account_id = self.__sts.get_caller_identity()["Account"]
        to_hash = self.seed + account_id + self.__sts.meta.region_name + body_hashes.decode()
        name_digest_input = BytesIO(to_hash.encode())
        body_hashes_hash = self.__digest(name_digest_input)
        return "formica-deploy-{}".format(body_hashes_hash)

    def upload(self):
        if not self.uploaded:
            s3 = boto3.resource("s3")
            self.uploaded = True
            self.s3_bucket = s3.Bucket(self.name)
            try:
                if self.__sts.meta.region_name == "us-east-1":
                    # To create a bucket in us-east-1 no LocationConstraint should be specified.
                    # See https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Bucket.create
                    self.s3_bucket.create()
                else:
                    self.s3_bucket.create(
                        CreateBucketConfiguration=dict(LocationConstraint=self.__sts.meta.region_name)
                    )
            except s3.meta.client.exceptions.BucketAlreadyOwnedByYou:
                logger.info("Artifact Bucket already exists")
            for name, body in self.objects.items():
                logger.info("Uploading to Bucket: {}/{}".format(self.name, name))
                self.s3_bucket.put_object(Key=name, Body=body)
            for name, file_name in self.files.items():
                with open(file_name, "rb") as f:
                    logger.info("Uploading to Bucket: {}/{}".format(self.name, name))
                    self.s3_bucket.put_object(Key=name, Body=f)


@contextmanager
def temporary_bucket(seed):
    temp_bucket = TemporaryS3Bucket(seed=seed)
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
