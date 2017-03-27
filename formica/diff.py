import collections
import re
from deepdiff import DeepDiff
from texttable import Texttable

from formica.aws_base import AWSBase
from formica.loader import Loader
import click

try:
    basestring
except NameError:
    basestring = str


class Change():
    def __init__(self, path, before, after, type):
        self.path = path
        self.before = before
        self.after = after
        self.type = type


def convert(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert, data.items()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert, data))
    else:
        return data


class Diff(AWSBase):
    def __init__(self, session):
        super(Diff, self).__init__(session)

    def run(self, stack):
        client = self.cf_client()

        result = client.get_template(
            StackName=stack,
        )

        loader = Loader()
        loader.load()

        changes = DeepDiff(convert(result['TemplateBody']), convert(loader.template_dictionary()), ignore_order=False,
                           report_repetition=True,
                           verbose_level=2, view='tree')

        table = Texttable(max_width=200)
        table.add_rows([['Path', 'From', 'To', 'Change Type']])
        print_diff = False

        processed_changes = self.__collect_changes(changes)

        for change in processed_changes:
            print_diff = True
            path = re.findall("\['?(\w+)'?\]", change.path)
            table.add_row(
                [
                    ' > '.join(path),
                    change.before,
                    change.after,
                    change.type.title().replace('_', ' ')
                ]
            )

        if print_diff:
            click.echo(table.draw() + "\n")
        else:
            click.echo('No Changes found')

    def __collect_changes(self, changes):
        results = []
        for key, value in changes.items():
            for change in list(value):
                results.append(Change(path=change.path(), before=change.t1, after=change.t2, type=key))
        return sorted(results, key=lambda x: x.path)
