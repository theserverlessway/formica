import subprocess
import uuid

import pytest


@pytest.fixture
def stack_name():
    return 'a' + str(uuid.uuid4())


class TestIntegrationBasic:
    def test_integration_basic(self, tmpdir, stack_name):
        def run_formica(*args):
            print(args)
            result = subprocess.run(['formica'] + list(args), stdout=subprocess.PIPE, check=True, cwd=tmpdir,
                                    encoding='utf-8')
            print(result.stdout)
            return result

        # Create a simple FC file and print it to STDOUT
        f = tmpdir.join("test.fc")
        f.write('resource(s3.Bucket("TestName"))')
        template = run_formica('template')
        assert 'TestName' in template.stdout
        assert 'AWS::S3::Bucket' in template.stdout

        stack_args = ['--stack', stack_name]

        # Create a ChangeSet for a new Stack to be deployed
        new = run_formica('new', *stack_args)
        assert 'AWS::S3::Bucket' in new.stdout

        # Deploy new Stack
        run_formica('deploy', *stack_args)

        f.write('resource(s3.Bucket("TestNameUpdate"))')

        # Change Resources in existing stack
        change = run_formica('change', *stack_args)
        assert 'TestNameUpdate' in change.stdout

        # Describe ChangeSet before deploying
        describe = run_formica('describe', *stack_args)
        assert 'TestNameUpdate' in describe.stdout

        # Deploy changes to existing stack
        deploy = run_formica('deploy', *stack_args)
        assert 'UPDATE_COMPLETE' in deploy.stdout

        # List all existing stacks
        stacks = run_formica('stacks')
        assert stack_name in stacks.stdout

        remove = run_formica('remove', *stack_args)
        assert 'DELETE_COMPLETE' in remove.stdout
