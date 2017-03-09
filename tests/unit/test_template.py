import json
import unittest

from click.testing import CliRunner

from formica import cli


class TestTemplate(unittest.TestCase):
    def test_template_calls_template(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with open('test.template.json', 'w') as f:
                f.write('{"Description": "{{ \'test\' | title }}"}')

            result = runner.invoke(cli.template)
            self.assertEqual(result.exit_code, 0)
            expected = {"Description": "Test"}
            self.assertEqual(json.loads(result.output), expected)
