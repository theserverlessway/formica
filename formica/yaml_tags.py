import yaml
from yaml.nodes import SequenceNode, CollectionNode
from yaml.resolver import BaseResolver


class BaseFunction(yaml.YAMLObject):
    @classmethod
    def tag(self, node):
        return node.lstrip('!')

    @classmethod
    def fn_tag(self, node):
        return 'Fn::' + self.tag(node)

    @classmethod
    def from_yaml(cls, loader, node):
        result = node.value
        kind = type(node)
        if isinstance(node, CollectionNode):
            if kind is SequenceNode:
                tag = BaseResolver.DEFAULT_SEQUENCE_TAG
            new_node = type(node)(tag, node.value)
            result = loader.construct_object(new_node, deep=True)
        return {cls.fn_tag(node.tag): result}


fn_functions = [
    'Base64', 'And', 'Equals', 'If', 'Not', 'Or', 'FindInMap', 'GetAZs', 'ImportValue', 'Join', 'Select',
    'Split', "Sub"
]

for function in fn_functions:
    type(function, (BaseFunction,), {'yaml_tag': '!' + function})


class SplitFunction(BaseFunction):
    @classmethod
    def from_yaml(cls, loader, node):
        return ({cls.fn_tag(node.tag): node.value.split('.')})


split_functions = [
    'GetAtt'
]

for function in split_functions:
    type(function, (SplitFunction,), {'yaml_tag': '!' + function})


class Ref(BaseFunction):
    yaml_tag = "!Ref"

    @classmethod
    def from_yaml(cls, loader, node):
        return {cls.tag(node.tag): node.value}
