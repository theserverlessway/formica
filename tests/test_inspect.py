import json
import unittest

from click.testing import CliRunner

from formica import cli


class TestInspect(unittest.TestCase):

    def test_inspect_calls_inspector(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with open('test.fc', 'w') as f:
                f.write('resource(s3.Bucket("TestName"))')

            result = runner.invoke(cli.inspect)
            self.assertEqual(result.exit_code, 0)
            expected = {'Resources': {'TestName': {'Type': 'AWS::S3::Bucket'}}}
            self.assertEqual(json.loads(result.output), expected)
