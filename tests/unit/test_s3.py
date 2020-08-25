from formica.s3 import temporary_bucket
import pytest



@pytest.fixture
def bucket(mocker):
    return mocker.patch('formica.s3.s3').Bucket



def test_s3_bucket_context(mocker, bucket, uuid4):
    key = "132413412341234"
    uuid4.return_value = key
    body = "test"

    bucket.return_value.objects.all.return_value = [mocker.Mock(key=key)]

    with temporary_bucket() as temp_bucket:
        temp_bucket.upload(body)

    bucket.assert_called_once()
    assert bucket.call_args[0][0].startswith('formica-deploy-')

    location_parameters = {'CreateBucketConfiguration': dict(LocationConstraint='eu-central-1')}

    bucket.return_value.create.assert_called_once_with(**location_parameters)
    bucket.return_value.put_object.assert_called_once_with(Body=body, Key=key)
    bucket.return_value.delete_objects.assert_called_once_with(Delete={'Objects': [{'Key': key}]})
    bucket.return_value.delete.assert_called_once_with()


def test_does_not_delete_objects_if_empty(mocker, bucket):
    bucket.return_value.objects.all.return_value = []

    with temporary_bucket():
        pass

    bucket.return_value.delete_objects.assert_not_called()
