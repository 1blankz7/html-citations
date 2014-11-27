import unittest
from pybtex.database.input import bibtex
from html_citation.citation_style import IEEEStyle
import io


TEST_BIBTEX = """
@Article{alexiadis2013real,
  Title                    = {Real-time, full 3-D reconstruction of moving foreground objects from multiple consumer depth cameras},
  Author                   = {Alexiadis, Dimitrios S and Zarpalas, Dimitrios and Daras},
  Journal                  = {IEEE Transactions on Multimedia},
  Year                     = {2013},
  Number                   = {2},
  Pages                    = {339--358},
  Volume                   = {15},

  Owner                    = {iwer},
  Publisher                = {IEEE},
  Timestamp                = {2014.10.20}
}
"""


class TestIEEEStyle(unittest.TestCase):

    def setUp(self):
        parser = bibtex.Parser()
        stream = io.StringIO(TEST_BIBTEX)
        self.entry = parser.parse_stream(stream).entries['alexiadis2013real']
        self.style = IEEEStyle()

    def test_format_name(self):
        author1 = self.entry.persons['Author'][0]
        author3 = self.entry.persons['Author'][2]
        self.assertEqual("D. Alexiadis", self.style.format_person(author1))
        self.assertEqual("Daras", self.style.format_person(author3))

    def test_format_doi(self):
        self.assertEqual(('doi', None), self.style.format_doi(self.entry))

    def test_format_names(self):
        self.assertEqual(
            "D. Alexiadis and D. Zarpalas and Daras",
            self.style.format_names(self.entry, "author")[1])

    def test_format_author_or_editor(self):
        self.assertEqual(
            ('authors', "D. Alexiadis and D. Zarpalas and Daras"),
            self.style.format_author_or_editor(self.entry))

    def test_format_editor(self):
        self.assertRaises(KeyError, self.style.format_editor, self.entry)

    def test_format_volume_and_series(self):
        self.fail()

    def test_format_chapter_and_pages(self):
        self.fail()

    def test_format_edition(self):
        self.fail()

    def test_format_date(self):
        self.fail()

    def test_format_title(self):
        self.fail()

    def test_format_address_organization_publisher_date(self):
        self.fail()

    def test_format_url(self):
        self.fail()

    def test_format_web_refs(self):
        self.fail()

    def test_format_article(self):
        self.fail()