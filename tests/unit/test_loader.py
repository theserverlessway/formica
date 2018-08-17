import json
import os

import pytest
import yaml
from path import Path

from formica.loader import Loader
from datetime import datetime, timedelta


@pytest.fixture()
def load():
    return Loader()


def write_and_test(example, load, tmpdir):
    with Path(tmpdir):
        with open('test.template.json', 'w') as f:
            f.write(json.dumps(example))
        load.load()
        actual = json.loads(load.template())
    assert actual == example


def test_supported_formats(load, tmpdir):
    json_example = {'Resources': {'TestJson': {'Type': 'AWS::S3::Bucket'}}}
    yaml_example = {'Resources': {'TestYaml': {'Type': 'AWS::S3::Bucket'}}}
    yml_example = {'Resources': {'TestYml': {'Type': 'AWS::S3::Bucket'}}}
    with Path(tmpdir):
        with open('test.template.json', 'w') as f:
            f.write(json.dumps(json_example))
        with open('test.template.yaml', 'w') as f:
            f.write(yaml.dump(yaml_example))
        with open('test.template.yml', 'w') as f:
            f.write(yaml.dump(yml_example))
        load.load()
        actual = json.loads(load.template())
    result = {'Resources': {'TestJson': {'Type': 'AWS::S3::Bucket'}, 'TestYaml': {'Type': 'AWS::S3::Bucket'},
                            'TestYml': {'Type': 'AWS::S3::Bucket'}}}
    assert actual == result


def test_successfully_adds_resources_to_template(load, tmpdir):
    example = {'Resources': {'TestName': {'Type': 'AWS::S3::Bucket'}}}
    write_and_test(example, load, tmpdir)


def test_successfully_adds_description_to_template(load, tmpdir):
    example = {'Description': 'TestDescription'}
    write_and_test(example, load, tmpdir)


def test_successfully_adds_metadata_to_template(load, tmpdir):
    example = {
        'Metadata': {
            'key': 'value',
            'key2': 'value2'}}
    write_and_test(example, load, tmpdir)


def test_successfully_adds_condition_to_template(load, tmpdir):
    example = {'Conditions': {'Condition1': {'Fn::Equals': [{'Ref': 'EnvType'}, 'prod']}}}
    write_and_test(example, load, tmpdir)


def test_successfully_adds_mapping_to_template(load, tmpdir):
    example = {'Mappings': {'RegionMap': {
        'us-east-1': {"AMI": "ami-7f418316"}}}}
    write_and_test(example, load, tmpdir)


def test_successfully_adds_parameter_to_template(load, tmpdir):
    example = {'Parameters': {'param': {'Type': 'String'}}}
    write_and_test(example, load, tmpdir)


def test_successfully_adds_output_to_template(load, tmpdir):
    example = {'Outputs': {'Output': {'Value': 'value'}}}
    write_and_test(example, load, tmpdir)


def test_supports_jinja_templates(load, tmpdir):
    example = '{"Description": "{{ \'test\' | title }}"}'
    with Path(tmpdir):
        with open('test.template.json', 'w') as f:
            f.write(example)
        load.load()
        actual = json.loads(load.template())
    assert actual == {"Description": "Test"}


def test_supports_extra_jinja_vars(tmpdir):
    load = Loader(variables={'test': 'bar'})
    example = '{"Description": "{{ test | title }}"}'
    with Path(tmpdir):
        with open('test.template.json', 'w') as f:
            f.write(example)
        load.load()
        actual = json.loads(load.template())
    assert actual == {"Description": "Bar"}


def test_module_vars_have_precedence_over_global(tmpdir):
    load = Loader(variables={'test': 'bar'})
    example = '{"Description": "{{ test }}"}'
    with Path(tmpdir):
        os.mkdir('moduledir')
        with open('moduledir/test.template.json', 'w') as f:
            f.write(example)
        with open('test.template.json', 'w') as f:
            f.write('{"Resources": {"TestResource": {"From": "Moduledir", "Properties": {"test": "baz" } }}}')
        load.load()
        actual = json.loads(load.template())
    assert actual == {"Description": "baz"}


def test_supports_resouce_command(load, tmpdir):
    example = '{"Description": "{{ \'ABC%123.\' | resource }}"}'
    with Path(tmpdir):
        with open('test.template.json', 'w') as f:
            f.write(example)
        load.load()
        actual = json.loads(load.template())
    assert actual == {"Description": "Abc123"}


def test_resouce_command_supports_none_value(load, tmpdir):
    example = '{"Description": "{{ None | resource }}"}'
    with Path(tmpdir):
        with open('test.template.json', 'w') as f:
            f.write(example)
        load.load()
        actual = json.loads(load.template())
    assert actual == {"Description": ""}


def test_template_loads_submodules(load, tmpdir):
    example = '{"Description": "{{ \'test\'}}"}'
    with Path(tmpdir):
        os.mkdir('moduledir')
        with open('moduledir/test.template.json', 'w') as f:
            f.write(example)
        with open('test.template.json', 'w') as f:
            f.write(json.dumps({'Resources': {'TestResource': {'From': 'Moduledir'}}}))
        load.load()
        actual = json.loads(load.template())
    assert actual == {"Description": "test"}


def test_template_loads_submodules_with_specific_file(load, tmpdir):
    example = '{"Description": "{{ \'test\'}}"}'
    with Path(tmpdir):
        os.mkdir('moduledir')
        with open('moduledir/test.template.json', 'w') as f:
            f.write(example)
        with open('moduledir/test2.template.yml', 'w') as f:
            f.write('Sometestthing: does not fail')
        with open('test.template.json', 'w') as f:
            f.write(json.dumps({'Resources': {'TestResource': {'From': 'Moduledir::Test'}}}))
        load.load()
        actual = json.loads(load.template())
    assert actual == {"Description": "test"}


def test_template_submodule_loads_variables(load, tmpdir):
    example = '{"Description": "{{ test }}"}'
    with Path(tmpdir):
        os.mkdir('moduledir')
        with open('moduledir/test.template.json', 'w') as f:
            f.write(example)
        with open('test.template.json', 'w') as f:
            f.write(json.dumps(
                {'Resources': {'TestResource':
                               {'From': 'Moduledir', 'Properties': {'test': 'Variable'}}}}))
        load.load()
        actual = json.loads(load.template())
    assert actual == {"Description": "Variable"}


def test_template_submodule_loads_further_modules(load, tmpdir):
    example = '{"Description": "Description"}'
    with Path(tmpdir):
        os.mkdir('moduledir')
        with open('moduledir/test.template.json', 'w') as f:
            f.write(example)
        with open('moduledir/module.template.json', 'w') as f:
            f.write(json.dumps({'Resources': {'TestResource': {'From': 'Test'}}}))
        with open('test.template.json', 'w') as f:
            f.write(json.dumps({'Resources': {'TestResource': {'From': 'Moduledir::Module'}}}))
        load.load()
        actual = json.loads(load.template())
    assert actual == {"Description": "Description"}


def test_template_fails_with_nonexistent_module(load, tmpdir):
    with Path(tmpdir):
        with open('test.template.json', 'w') as f:
            f.write(json.dumps({'Resources': {'TestResource': {'From': 'Moduledir'}}}))
        with pytest.raises(SystemExit):
            load.load()


def test_template_fails_with_no_files_in_module(load, tmpdir):
    with Path(tmpdir):
        os.mkdir('moduledir')
        with open('test.template.json', 'w') as f:
            f.write(json.dumps({'Resources': {'TestResource': {'From': 'Moduledir'}}}))
        with pytest.raises(SystemExit):
            load.load()


def test_template_fails_with_no_file_in_module_with_specified_template(load, tmpdir):
    with Path(tmpdir):
        os.mkdir('moduledir')
        with open('test.template.json', 'w') as f:
            f.write(json.dumps({'Resources': {'TestResource': {'From': 'Moduledir::Test'}}}))
        with pytest.raises(SystemExit):
            load.load()


def test_template_ignores_empty_module(load, tmpdir):
    with Path(tmpdir):
        os.mkdir('moduledir')
        with open('moduledir/test.template.json', 'w') as f:
            f.write('')
        with open('test.template.json', 'w') as f:
            f.write(json.dumps({'Resources': {'TestResource': {'From': 'Moduledir::Test'}}}))
        load.load()


def test_template_syntax_exception_gets_caught(load, tmpdir):
    example = '{"Description": "{{ test }"}'
    with Path(tmpdir):
        with open('test.template.json', 'w') as f:
            f.write(example)
        with pytest.raises(SystemExit):
            load.load()


def test_template_comment_exception_gets_caught(load, tmpdir):
    example = '{"Description": "{#test}"}'
    with Path(tmpdir):
        with open('test.template.json', 'w') as f:
            f.write(example)
        with pytest.raises(SystemExit):
            load.load()


def test_template_not_found_exception_gets_caught(load, tmpdir):
    example = '{"Description": "{{ code(\'testfile\') }}}'
    with Path(tmpdir):
        with open('test.template.json', 'w') as f:
            f.write(example)
        with pytest.raises(SystemExit):
            load.load()


def test_yaml_json_syntax_exception_gets_caught(load, tmpdir):
    example = '{"Description: "Description"}'
    with Path(tmpdir):
        with open('test.template.json', 'w') as f:
            f.write(example)
        with pytest.raises(SystemExit):
            load.load()


def test_mandatory_filter_throws_exception(load, tmpdir):
    example = '{"Description": "{{ test | mandatory }}"}'
    with Path(tmpdir):
        with open('test.template.json', 'w') as f:
            f.write(example)
        with pytest.raises(SystemExit):
            load.load()


def test_mandatory_filter_throws_exception_in_module(load, tmpdir):
    example = '{"Description": "{{ test | mandatory }}"}'
    with Path(tmpdir):
        os.mkdir('moduledir')
        with open('moduledir/test.template.json', 'w') as f:
            f.write(example)
        with open('test.template.json', 'w') as f:
            f.write('{"Resources": {"TestResource": {"From": "Moduledir::Test", "Properties": {"test":{{ test }}}}}}')
        with pytest.raises(SystemExit):
            load.load()


def test_wrong_key_throws_exception(load, tmpdir):
    example = '{"SomeKey": "test"}'
    with Path(tmpdir):
        with open('test.template.json', 'w') as f:
            f.write(example)
        with pytest.raises(SystemExit):
            load.load()


def test_mandatory_filter_passes_through_text(load, tmpdir):
    example = '{"Description": "{{ "test" | mandatory }}"}'
    with Path(tmpdir):
        with open('test.template.json', 'w') as f:
            f.write(example)
        load.load()
        actual = json.loads(load.template())
    assert actual == {"Description": "test"}


def test_code_includes_and_escapes_code(load, tmpdir):
    example = '{"Description": "{{ code("test.py") }}"}'
    pycode = "test\n\"something\""
    with Path(tmpdir):
        with open('test.template.json', 'w') as f:
            f.write(example)
        with open('test.py', 'w') as f:
            f.write(pycode)
        load.load()
        actual = json.loads(load.template())
    assert actual == {"Description": "test\n\"something\""}


def test_code_allows_to_include_files_from_parent(load, tmpdir):
    parent = '{"Resources": {"Test": {"From": "Moduledir"}}}'
    module = '{"Description": "{{ code("../test.txt") }}"}'
    description = "someDescription"
    with Path(tmpdir):
        os.mkdir('moduledir')
        with open('test.template.json', 'w') as f:
            f.write(parent)
        with open('moduledir/test.template.json', 'w') as f:
            f.write(module)
        with open('test.txt', 'w') as f:
            f.write(description)
        load.load()
        actual = json.loads(load.template())
    assert actual == {"Description": description}


def test_code_includes_additional_variables(load, tmpdir):
    example = '{"Description": "{{ code("test.py", testvar=\'teststring\') }}"}'
    pycode = "test\n{{testvar}}"
    with Path(tmpdir):
        with open('test.template.json', 'w') as f:
            f.write(example)
        with open('test.py', 'w') as f:
            f.write(pycode)
        load.load()
        actual = json.loads(load.template())
    assert actual == {"Description": "test\nteststring"}


def test_code_includes_supports_nested_code_arguments(load, tmpdir):
    example = '{% set nested_var = "nested" %}{"Description": "{{ code("test.one", nested_var=nested_var) }}"}'
    one = '{{ code("test.two", nested_var=nested_var) }}'
    two = '{{ nested_var }}-test'
    with Path(tmpdir):
        with open('test.template.json', 'w') as f:
            f.write(example)
        with open('test.one', 'w') as f:
            f.write(one)
        with open('test.two', 'w') as f:
            f.write(two)
        load.load()
        actual = json.loads(load.template())
    assert actual == {"Description": "nested-test"}


def test_novalue_uses_value_if_given(load, tmpdir):
    example = '{% set Parameter = "description" %}{"Description": "{{ Parameter | novalue }}"}'
    with Path(tmpdir):
        with open('test.template.json', 'w') as f:
            f.write(example)
        load.load()
        actual = json.loads(load.template())
    assert actual == {"Description": "description"}


def test_novalue_uses_pseudoparameter_novalue_for_missing_variable(load, tmpdir):
    example = '{"Resources": {{ Parameter | novalue }}}'
    with Path(tmpdir):
        with open('test.template.json', 'w') as f:
            f.write(example)
        load.load()
        actual = json.loads(load.template())
    assert actual == {"Resources": {"Ref": "AWS::NoValue"}}


def test_un_indented_large_templates(load):
    # Generate a large dictionary that, with indent=4, is too large to deploy
    # as a template. Loader supports passing the `indent` param as `None` to
    # remove indentation.
    load.cftemplate = {'Resources': {i: 'a' * 84 for i in range(512)}}
    assert len(load.template()) > 51200
    assert len(load.template(indent=None)) < 51200


def test_now(load, tmpdir):
    example = '{"Resources": {"Test": "{{ now().shift(days=1).format("YYYY-MM-DD HH:mm") }}"}}'
    with Path(tmpdir):
        with open('test.template.json', 'w') as f:
            f.write(example)
        load.load()
        print(load.template())
        actual = json.loads(load.template())
    assert actual == {"Resources": {"Test": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M")}}


def test_utcnow(load, tmpdir):
    example = '{"Resources": {"Test": "{{ utcnow().shift(days=1).format("YYYY-MM-DD HH:mm") }}"}}'
    with Path(tmpdir):
        with open('test.template.json', 'w') as f:
            f.write(example)
        load.load()
        print(load.template())
        actual = json.loads(load.template())
    assert actual == {"Resources": {"Test": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M")}}
