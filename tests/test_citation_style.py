__author__ = 'christian'

import unittest
import citation_style


class E:
    pass


if_next = citation_style.if_next
optional = citation_style.optional
get = citation_style.get
present = citation_style.present
flat = citation_style.flat


class TestCitationStyle(unittest.TestCase):

    def test_get(self):
        entry = E()
        entry.fields = {'foo': 1}

        self.assertEquals(('foo', 1), get(entry, 'foo'))
        self.assertRaises(KeyError, get, entry, 'bar')
        self.assertEquals(('foo', 2), get(entry, 'foo', apply_func= lambda x: 2*x))

    def test_if_next(self):
        self.assertEquals((None, "+"), if_next("+")(('foo', 1)))
        self.assertFalse((None, "+") == if_next("+")(('foo', None)))


    def test_optional(self):
        entry = E()
        entry.fields = {'foo': 1}

        self.assertEquals(('foo', 1), optional(entry, 'foo'))
        self.assertEquals(('bar', None), optional(entry, 'bar'))

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
        self.assertEquals("Hello1", "".join([str(v[1]) for v in flat(data)]))
        data = [
            if_next("Hello"),
            optional(entry, 'foo'),
            if_next("World"),
            optional(entry, 'bar')
        ]
        flatted = flat(data)
        flatted = list(flatted)
        self.assertEquals("Hello1", "".join([str(v[1]) for v in flatted]))
        data = [
            if_next("Hello"),
            optional(entry, 'bar'),
            if_next("World"),
            optional(entry, 'foo')
        ]
        self.assertEquals("", "".join([str(v[1]) for v in flat(data)]))
