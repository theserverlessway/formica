from formica.s3 import temporary_bucket
import pytest


@pytest.fixture
def bucket(mocker, boto_resource, boto_client):
    return boto_resource.return_value.Bucket


STRING_BODY = "string"
# MD5 has of body
STRING_KEY = "b45cffe084dd3d20d928bee85e7b0f21"
BINARY_BODY = "binary".encode()
BINARY_KEY = "9d7183f16acce70658f686ae7f1a4d20"
BUCKET_NAME = "formica-deploy-2d76d05dc575a9e10d346fde56909c20"


def test_s3_bucket_context(mocker, bucket, uuid4, boto_client):
    bucket.return_value.objects.all.return_value = [mocker.Mock(key=STRING_KEY), mocker.Mock(key=BINARY_KEY)]
    boto_client.return_value.meta.region_name = "eu-central-1"
    boto_client.return_value.get_caller_identity.return_value = {'Account': '1234'}

    with temporary_bucket() as temp_bucket:
        string_return = temp_bucket.add(STRING_BODY)
        binary_return = temp_bucket.add(BINARY_BODY)
        temp_bucket.upload()
        bucket_name = temp_bucket.name

    assert string_return == STRING_KEY
    assert binary_return == BINARY_KEY
    assert bucket_name == BUCKET_NAME
    bucket.assert_called_once_with(BUCKET_NAME)
    assert bucket.call_count == 1

    location_parameters = {'CreateBucketConfiguration': dict(LocationConstraint='eu-central-1')}

    calls = [mocker.call(Body=STRING_BODY.encode(), Key=STRING_KEY), mocker.call(Body=BINARY_BODY, Key=BINARY_KEY)]
    bucket.return_value.create.assert_called_once_with(**location_parameters)
    bucket.return_value.put_object.assert_has_calls(calls)
    assert bucket.return_value.put_object.call_count == 2
    bucket.return_value.delete_objects.assert_called_once_with(
        Delete={'Objects': [{'Key': STRING_KEY}, {'Key': BINARY_KEY}]})
    bucket.return_value.delete.assert_called_once_with()


def test_does_not_delete_objects_if_empty(mocker, bucket):
    bucket.return_value.objects.all.return_value = []

    with temporary_bucket():
        pass

    bucket.return_value.delete_objects.assert_not_called()


def test_does_not_use_s3_api_when_planning(mocker, bucket):
    bucket.return_value.objects.all.return_value = []

    with temporary_bucket() as temp_bucket:
        temp_bucket.add(STRING_BODY)
        temp_bucket.add(BINARY_BODY)

    bucket.return_value.create.assert_not_called()
    bucket.return_value.put_object.assert_not_called()
    bucket.return_value.delete_objects.assert_not_called()
