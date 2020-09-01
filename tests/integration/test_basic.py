import subprocess
import uuid
import json
import yaml
from path import Path

import pytest


@pytest.fixture
def stack_name():
    return 'formica-it-' + str(uuid.uuid4())


CONFIG_FILE = 'test.config.json'

TEMPLATE_FILE = """
Resources:
  TestName:
    Type: AWS::S3::Bucket
    Properties:
      Tags:
        - Key: Bucket
          Value: {{ artifacts['SomeArtifact'].bucket }}
        - Key: Name
          Value: {{ artifacts['SomeArtifact'].key }}
"""


class TestIntegrationBasic():
    def test_integration_basic(self, tmpdir, stack_name):
        with Path(tmpdir):
            def run_formica(*args):
                print()
                print("Command: formica {}".format(' '.join(args)))
                result = subprocess.check_output(['formica'] + list(args), cwd=str(tmpdir)).decode()
                print(result)
                return result

            def write_template(content):
                with open("test.template.json", 'w') as f:
                    f.write(content)

            def write_config(content):
                with open(CONFIG_FILE, 'w') as f:
                    f.write(json.dumps(content))

            # Create a simple FC file and print it to STDOUT
            write_template(TEMPLATE_FILE)
            write_config({'stack': stack_name, "artifacts": ['SomeArtifact']})
            with open("SomeArtifact", 'w') as f:
                f.write("Artifact")

            artifacts_args = ['--artifacts', 'SomeArtifact']

            template = run_formica('template', *artifacts_args)
            assert 'TestName' in template
            assert 'AWS::S3::Bucket' in template

            stack_args = ['--stack', stack_name]

            stack_artifact_args = [*stack_args, *artifacts_args]

            # Create a ChangeSet for a new Stack to be deployed
            new = run_formica('new', *stack_artifact_args)
            assert 'AWS::S3::Bucket' in new

            # Deploy new Stack
            run_formica('deploy', '-c', CONFIG_FILE)

            write_template(json.dumps({'Resources': {'TestNameUpdate': {'Type': 'AWS::S3::Bucket'}}}))

            # Diff the current stack
            diff = run_formica('diff', *stack_artifact_args)

            assert 'Resources > TestName' in diff
            assert 'Dictionary Item Removed' in diff
            assert 'Resources > TestNameUpdate' in diff
            assert 'Dictionary Item Added' in diff

            # Change Resources in existing stack
            change = run_formica('change', '--s3', *stack_artifact_args)
            assert 'TestNameUpdate' in change

            # Describe ChangeSet before deploying
            describe = run_formica('describe', *stack_args)
            assert 'TestNameUpdate' in describe

            # Deploy changes to existing stack
            deploy = run_formica('deploy', *stack_artifact_args)
            assert 'UPDATE_COMPLETE' in deploy

            # Add Changes again without failing
            change = run_formica('change', *stack_artifact_args)
            assert "The submitted information didn't contain changes." in change

            # List Resources after deployment
            resources = run_formica('resources', *stack_args)
            assert 'TestNameUpdate' in resources

            # List all existing stacks
            stacks = run_formica('stacks')
            assert stack_name in stacks

            remove = run_formica('remove', *stack_args)
            assert 'DELETE_COMPLETE' in remove
