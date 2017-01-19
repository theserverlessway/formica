import unittest
from formica import helper

class TestTemplate(unittest.TestCase):
    def test_name_titelizes(self):
        self.assertEqual(helper.name('test'), 'Test')

    def test_name_removes_special_characters(self):
        self.assertEqual(helper.name('.test%'), 'Test')
