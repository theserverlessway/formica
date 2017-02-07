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

    def test_template_syntax_exception_gets_caught(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with open('main.fc', 'w') as f:
                f.write('module("moduledir')

            result = runner.invoke(cli.show)
            self.assertEqual(result.exit_code, 1)
            self.assertIn('main.fc", line 1, char 18', result.output)
            self.assertIn('SyntaxError: EOL while scanning string literal', result.output)
            self.assertIn(' ^\n', result.output)

    def test_template_exception_gets_caught(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with open('main.fc', 'w') as f:
                f.write('module("moduledir" + randomvariable)')

            result = runner.invoke(cli.show)
            self.assertEqual(result.exit_code, 1)
            self.assertIn('main.fc", line 1', result.output)
            self.assertIn('NameError: name \'randomvariable\' is not defined', result.output)
