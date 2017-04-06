import os
import re


def test_validate_examples_are_linked():
    examples_directory = 'docs/examples'

    with open('docs/README.md') as file:
        documentation = file.read()
    for dir in os.listdir(examples_directory):
        to_find = '\(examples/{}\)'
        assert re.search(to_find.format(dir), documentation)
