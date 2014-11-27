__author__ = 'christian'

import unittest
from html_citation.citation_style import (if_next, optional, html,
                              get, present, if_prev_and_next, flat)


class E:
    pass


class TestCitationStyle(unittest.TestCase):

    def test_get(self):
        entry = E()
        entry.fields = {'foo': 1}

        self.assertEqual(('foo', 1), get(entry, 'foo'))
        self.assertRaises(KeyError, get, entry, 'bar')
        self.assertEqual(('foo', 2), get(entry, 'foo', apply_func= lambda x: 2*x))

    def test_if_next(self):
        self.assertEqual((None, "+"), if_next("+")(('foo', 1), None))
        self.assertFalse((None, "+") == if_next("+")(('foo', None), None))

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
            if_prev_and_next("World"),
            optional(entry, 'foo')
        ]
        self.assertEqual("1", "".join([str(v[1]) for v in flat(data)]))

    def test_html(self):
        entry = E()
        entry.label = '1'
        entry.text = [
            ('authors', 'D. Alexiadis and D. Zarpalas and Daras'),
            ('title', '"Real-time, full 3-d reconstruction of moving foreground objects from multiple consumer depth cameras"'),
            ('journal', 'IEEE Transactions on Multimedia'),
            [('volume', '15'), ('number', '(2)'), (None, ':'), ('pages', '339--358')],
            [('month', None), ('year', '2013')],
            [('url', None), ('doi', None)]
        ]
        self.assertEqual("", html(entry))
