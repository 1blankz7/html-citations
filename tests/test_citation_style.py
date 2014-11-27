__author__ = 'christian'

import unittest
import html_citation.citation_style as cs


class E:
    pass


if_next = cs.if_next
optional = cs.optional
get = cs.get
present = cs.present
flat = cs.flat


class TestCitationStyle(unittest.TestCase):

    def test_get(self):
        entry = E()
        entry.fields = {'foo': 1}

        self.assertEqual(('foo', 1), get(entry, 'foo'))
        self.assertRaises(KeyError, get, entry, 'bar')
        self.assertEqual(('foo', 2), get(entry, 'foo', apply_func= lambda x: 2*x))

    def test_if_next(self):
        self.assertEqual((None, "+"), if_next("+")(('foo', 1)))
        self.assertFalse((None, "+") == if_next("+")(('foo', None)))

    def test_optional(self):
        entry = E()
        entry.fields = {'foo': 1}

        self.assertEqual(('foo', 1), optional(entry, 'foo'))
        self.assertEqual(('bar', None), optional(entry, 'bar'))

    def test_present(self):
        self.assertTrue(present(('foo', 1)))
        self.assertTrue(present((None, "str")))
        self.assertFalse(present(('foo', None)))
        self.assertFalse(present((None, None)))

    def test_flat(self):
        entry = E()
        entry.fields = {'foo': 1}
        data = [
            if_next("Hello"),
            optional(entry, 'foo')
        ]
        self.assertEqual("Hello1", "".join([str(v[1]) for v in flat(data)]))
        data = [
            if_next("Hello"),
            optional(entry, 'foo'),
            if_next("World"),
            optional(entry, 'bar')
        ]
        flatted = flat(data)
        flatted = list(flatted)
        self.assertEqual("Hello1", "".join([str(v[1]) for v in flatted]))
        data = [
            if_next("Hello"),
            optional(entry, 'bar'),
            if_next("World"),
            optional(entry, 'foo')
        ]
        self.assertEqual("", "".join([str(v[1]) for v in flat(data)]))
