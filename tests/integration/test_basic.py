import subprocess
import uuid
import json
from path import Path

import pytest


@pytest.fixture
def stack_name():
    return 'a' + str(uuid.uuid4())


CONFIG_FILE = 'test.config.json'


class TestIntegrationBasic():
    def test_integration_basic(self, tmpdir, stack_name):
        with Path(tmpdir):
            def run_formica(*args):
                result = str(subprocess.check_output(['formica'] + list(args), cwd=str(tmpdir)))

                return result

            def write_template(content):
                with open("test.template.json", 'w') as f:
                    f.write(json.dumps(content))

            def write_config(content):
                with open(CONFIG_FILE, 'w') as f:
                    f.write(json.dumps(content))

            # Create a simple FC file and print it to STDOUT
            write_template({'Resources': {'TestName': {'Type': 'AWS::S3::Bucket'}}})
            write_config({'stack': stack_name})
            template = run_formica('template')
            assert 'TestName' in template
            assert 'AWS::S3::Bucket' in template

            stack_args = ['--stack', stack_name]

            # Create a ChangeSet for a new Stack to be deployed
            new = run_formica('new', *stack_args)
            assert 'AWS::S3::Bucket' in new

            # Deploy new Stack
            run_formica('deploy', '-c', CONFIG_FILE)

            write_template({'Resources': {'TestNameUpdate': {'Type': 'AWS::S3::Bucket'}}})

            # Diff the current stack
            diff = run_formica('diff', *stack_args)

            assert 'Resources > TestName' in diff
            assert 'Dictionary Item Removed' in diff
            assert 'Resources > TestNameUpdate' in diff
            assert 'Dictionary Item Added' in diff

            # Change Resources in existing stack
            change = run_formica('change', '--s3', *stack_args)
            assert 'TestNameUpdate' in change

            # Describe ChangeSet before deploying
            describe = run_formica('describe', *stack_args)
            assert 'TestNameUpdate' in describe

            # Deploy changes to existing stack
            deploy = run_formica('deploy', *stack_args)
            assert 'UPDATE_COMPLETE' in deploy

            # Add Changes again without failing
            change = run_formica('change', *stack_args)
            assert "The submitted information didn't contain changes." in change

            # List Resources after deployment
            resources = run_formica('resources', *stack_args)
            assert 'TestNameUpdate' in resources

            # List all existing stacks
            stacks = run_formica('stacks')
            assert stack_name in stacks

            remove = run_formica('remove', *stack_args)
            assert 'DELETE_COMPLETE' in remove
