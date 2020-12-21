import pytest

from formica import helper


def test_with_artifacts(mocker, temp_bucket):
    class Namespace:
        def __init__(self):
            self.artifacts = ['file1']

    print(temp_bucket)
    function = mocker.Mock()
    func = helper.with_artifacts(function)
    n = Namespace()
    print(n.artifacts)
    func(n)
    temp_bucket.add_file.assert_called_with('file1')
    temp_bucket.upload.assert_called()
    function.assert_called_with(n)


def test_with_artifacts_with_empty_artifacts(mocker):
    class Namespace:
        def __init__(self):
            self.artifacts = []

    t = mocker.patch('formica.helper.temporary_bucket')
    function = mocker.Mock()
    func = helper.with_artifacts(function)
    n = Namespace()
    func(n)
    t.assert_not_called()
    function.assert_called_with(n)
