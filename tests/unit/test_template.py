from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import open
from future import standard_library
standard_library.install_aliases()
import json
import os
import unittest

from click.testing import CliRunner

from formica import cli


class TestTemplate(unittest.TestCase):
    def test_template_calls_inspector(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with open('test.fc', 'w') as f:
                f.write(u'resource(s3.Bucket("TestName"))')

            result = runner.invoke(cli.template)
            self.assertEqual(result.exit_code, 0)
            expected = {'Resources': {'TestName': {'Type': 'AWS::S3::Bucket'}}}
            self.assertEqual(json.loads(result.output), expected)

    def test_template_loads_submodules(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.mkdir('moduledir')
            with open('main.fc', 'w') as f:
                f.write(u'module("moduledir")')
            with open('moduledir/test.fc', 'w') as f:
                f.write(u'resource(s3.Bucket("TestName"))')

            result = runner.invoke(cli.template)
            expected = {'Resources': {'TestName': {'Type': 'AWS::S3::Bucket'}}}
            actual = json.loads(result.output)
            self.assertEqual(actual, expected)

    def test_template_syntax_exception_gets_caught(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with open('main.fc', 'w') as f:
                f.write(u'module("moduledir')

            result = runner.invoke(cli.template)
            self.assertEqual(result.exit_code, 1)
            self.assertIn('main.fc", line 1, char 1', result.output)
            self.assertIn(u'SyntaxError: EOL while scanning string literal', result.output)
            self.assertIn(u' ^\n', result.output)

    def test_template_exception_gets_caught(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with open('main.fc', 'w') as f:
                f.write(u'module("moduledir" + randomvariable)')

            result = runner.invoke(cli.template)
            self.assertEqual(result.exit_code, 1)
            self.assertIn('main.fc", line 1', result.output)
            self.assertIn('NameError: name \'randomvariable\' is not defined', result.output)
