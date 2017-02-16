
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
import unittest

from formica import helper


class TestHelper(unittest.TestCase):

    def test_name_titelizes(self):
        self.assertEqual(helper.name('test'), 'Test')

    def test_name_removes_special_characters(self):
        self.assertEqual(helper.name('.test%'), 'Test')
