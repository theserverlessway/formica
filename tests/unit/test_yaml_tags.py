import pytest
from path import Path

from formica.loader import Loader


@pytest.fixture()
def loader():
    return Loader()


@pytest.fixture()
def runner(loader, tmpdir):
    def validate(yaml, expect):
        with Path(tmpdir):
            with open('test.template.yaml', 'w') as f:
                f.write(yaml)
            loader.load()
        assert loader.template_dictionary() == expect

    return validate


@pytest.mark.parametrize('input,expected', [
    ('Resources: !Base64 something', {'Resources': {"Fn::Base64": 'something'}}),
    ('Resources: !And [ !Equals ["a", "b"], !Equals ["c", "d"], ] ',
     {'Resources': {"Fn::And": [{"Fn::Equals": ['a', 'b']}, {"Fn::Equals": ['c', 'd']}]}}),
    ('Resources: !If [A, !Ref B, !Ref C]', {'Resources': {"Fn::If": ['A', {"Ref": "B"}, {"Ref": "C"}]}}),
    ('Resources: !Not [!Equals [!Ref A, prod]]', {'Resources': {"Fn::Not": [{'Fn::Equals': [{"Ref": "A"}, "prod"]}]}}),
    ('Resources: !Or [ !Equals ["a", "b"], !Equals ["c", "d"], ] ',
     {'Resources': {"Fn::Or": [{"Fn::Equals": ['a', 'b']}, {"Fn::Equals": ['c', 'd']}]}}),
    ('Resources: !FindInMap [ RegionMap, !Ref "A", 32 ]',
     {'Resources': {"Fn::FindInMap": ['RegionMap', {"Ref": "A"}, 32]}}),
    ('Resources: !GetAtt A.B', {'Resources': {"Fn::GetAtt": ['A', 'B']}}),
    ('Resources: !GetAtt A.B.C', {'Resources': {"Fn::GetAtt": ['A', 'B.C']}}),
    ('Resources: !GetAZs us-east-1', {'Resources': {"Fn::GetAZs": 'us-east-1'}}),
    ('Resources: !ImportValue ABC', {'Resources': {"Fn::ImportValue": 'ABC'}}),
    ('Resources: !Join ["", "A", "B"]', {'Resources': {"Fn::Join": ['', 'A', 'B']}}),
    ('Resources: !Select [1, ["A", "B"]]', {'Resources': {"Fn::Select": [1, ['A', 'B']]}}),
    ('Resources: !Split ["." , "A.B" ]', {'Resources': {"Fn::Split": ['.', 'A.B']}}),
    ('Resources: !Sub ["${String}", {A: B} ]', {'Resources': {"Fn::Sub": ['${String}', {"A": "B"}]}}),
    ('Resources: !Ref ABC', {'Resources': {"Ref": 'ABC'}}),
    ('Resources: !GetAZs\n           Ref: AWS::Region', {'Resources': {'Fn::GetAZs': {"Ref": 'AWS::Region'}}}),
    ('Resources: !GetAtt ["abc", "def"]', {'Resources': {'Fn::GetAtt': ['abc', 'def']}}),
    ('Resources: !Condition TestCondition', {'Resources': {'Condition': 'TestCondition'}}),
    ('Resources: !Cidr [ "A", "B", "C" ]', {'Resources': {'Fn::Cidr': [ "A", "B", "C" ]}}),



])
def test_yaml_tag(runner, input, expected):
    runner(input, expected)
