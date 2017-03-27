import subprocess
import uuid
import json

import pytest


@pytest.fixture
def stack_name():
    return 'a' + str(uuid.uuid4())


class TestIntegrationBasic():
    def test_integration_basic(self, tmpdir, stack_name):
        def run_formica(*args):
            print(args)
            result = str(subprocess.check_output(['formica'] + list(args), cwd=str(tmpdir)))
            print(result)
            return result

        # Create a simple FC file and print it to STDOUT
        f = tmpdir.join("test.template.json")
        f.write(json.dumps({'Resources': {'TestName': {'Type': 'AWS::S3::Bucket'}}}))
        template = run_formica('template')
        assert 'TestName' in template
        assert 'AWS::S3::Bucket' in template

        stack_args = ['--stack', stack_name]

        # Create a ChangeSet for a new Stack to be deployed
        new = run_formica('new', *stack_args)
        assert 'AWS::S3::Bucket' in new

        # Deploy new Stack
        run_formica('deploy', *stack_args)

        f.write(json.dumps({'Resources': {'TestNameUpdate': {'Type': 'AWS::S3::Bucket'}}}))

        # Diff the current stack
        diff = run_formica('diff', *stack_args)
        print(diff)
        assert 'Resources > TestName' in diff
        assert 'Dictionary Item Removed' in diff
        assert 'Resources > TestNameUpdate' in diff
        assert 'Dictionary Item Added' in diff

        # Change Resources in existing stack
        change = run_formica('change', *stack_args)
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
