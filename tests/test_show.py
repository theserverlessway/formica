import json
import os
import unittest

from click.testing import CliRunner

from formica import cli


class TestShow(unittest.TestCase):
    def test_inspect_calls_inspector(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with open('test.fc', 'w') as f:
                f.write('resource(s3.Bucket("TestName"))')

            result = runner.invoke(cli.show)
            self.assertEqual(result.exit_code, 0)
            expected = {'Resources': {'TestName': {'Type': 'AWS::S3::Bucket'}}}
            self.assertEqual(json.loads(result.output), expected)

    def test_show_loads_submodules(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.mkdir('moduledir')
            with open('main.fc', 'w') as f:
                f.write('module("moduledir")')
            with open('moduledir/test.fc', 'w') as f:
                f.write('resource(s3.Bucket("TestName"))')

            result = runner.invoke(cli.show)
            expected = {'Resources': {'TestName': {'Type': 'AWS::S3::Bucket'}}}
            actual = json.loads(result.output)
            self.assertEqual(actual, expected)
