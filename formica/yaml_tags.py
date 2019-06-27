import yaml
from yaml.nodes import SequenceNode, ScalarNode, MappingNode, CollectionNode
from yaml.resolver import BaseResolver


class BaseFunction(yaml.YAMLObject):
    @classmethod
    def tag(self, node):
        return node.lstrip("!")

    @classmethod
    def fn_tag(self, node):
        return "Fn::" + self.tag(node)

    @classmethod
    def from_yaml(cls, loader, node):
        result = node.value
        kind = type(node)
        if isinstance(node, CollectionNode):
            if kind is SequenceNode:
                tag = BaseResolver.DEFAULT_SEQUENCE_TAG
            elif kind is MappingNode:
                tag = BaseResolver.DEFAULT_MAPPING_TAG
            new_node = type(node)(tag, node.value)
            result = loader.construct_object(new_node, deep=True)
        return {cls.fn_tag(node.tag): result}


def create_classes(functions, base_type=BaseFunction):
    for function in functions:
        type(function, (base_type,), {"yaml_tag": "!" + function})


fn_functions = [
    "Base64",
    "And",
    "Equals",
    "If",
    "Not",
    "Or",
    "FindInMap",
    "GetAZs",
    "ImportValue",
    "Join",
    "Select",
    "Split",
    "Sub",
    "Cidr",
]

create_classes(fn_functions)


class SplitFunction(BaseFunction):
    @classmethod
    def from_yaml(cls, loader, node):
        if type(node) is ScalarNode:
            result = node.value.split(".", 1)
        else:
            result = [loader.construct_object(child, deep=True) for child in node.value]
        return {cls.fn_tag(node.tag): result}


split_functions = ["GetAtt"]

create_classes(split_functions, SplitFunction)

non_fn_functions = ["Ref", "Condition"]


class NonFnFunction(BaseFunction):
    @classmethod
    def from_yaml(cls, loader, node):
        return {cls.tag(node.tag): node.value}


create_classes(non_fn_functions, NonFnFunction)
