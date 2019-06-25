import os
import re


def test_validate_examples_are_linked():
    examples_directory = 'docs/examples'

    with open('docs/examples.md') as file:
        documentation = file.read()
    for dir in os.listdir(examples_directory):
        to_find = '(https://github.com/theserverlessway/formica/tree/master/docs/examples/{})'.format(dir)
        assert to_find in documentation
