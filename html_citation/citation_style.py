from lxml.html import builder as E
from pybtex.style.formatting import BaseStyle
import types


def get(entry, field, apply_func=None):
    e = entry.fields[field]
    if apply_func is not None:
        e = apply_func(e)
    return field, e


def if_next(value):
    def f(n, m):
        return (None, str(value)) if present(n) else None

    return f


def if_prev_and_next(value):
    def f(n, m):
        return (None, str(value)) if present(n) and present(m) else None

    return f


def optional(entry, field, apply_func=None):
    try:
        return get(entry, field, apply_func)
    except KeyError:
        return field, None


def present(opt):
    if type(opt) == list:
        for el in opt[:2]:
            if not isinstance(el, types.FunctionType):
                return present(el)
    elif type(opt) == tuple:
        return opt[1] is not None


def flat(opt_arr):
    text = []
    for idx in range(len(opt_arr)):
        el = opt_arr[idx]
        if isinstance(el, types.FunctionType):
            func_res = el(opt_arr[idx + 1], opt_arr[idx - 1] if idx > 0 else None)
            if func_res is not None:
                text.append(func_res)
            else:
                continue
        else:
            text.append(el)
    return list(filter(lambda x: x[1] is not None, text))


class IEEEStyle(BaseStyle):
    """
    """

    def format_person(self, person):
        first = person.get_part_as_text('first')
        last = person.get_part_as_text('last')
        if len(first) > 0 and len(last) > 0:
            return "%s. %s" % (first[0], last)
        elif len(last) > 0:
            return last
        else:
            return None

    def format_doi(self, e):
        return optional(e, 'doi')

    def format_names(self, e, role):
        text = ""

        names = list([self.format_person(a) for a in e.persons[role]])

        if len(names) > 0:
            text = " and ".join(names)
            return ('authors', text)
        else:
            return (None, None)

    def format_author_or_editor(self, e):
        author = self.format_names(e, 'author')
        if not present(author):
            return self.format_editor(e)
        else:
            return author

    def format_editor(self, e):
        editors = self.format_names(e, 'editor')
        if 'editor' not in e.persons:
            # when parsing the template, a FieldIsMissing exception
            # will be thrown anyway; no need to do anything now,
            # just return the template that will throw the exception
            return editors
        if len(e.persons['editor']) > 1:
            word = 'editors'
        else:
            word = 'editor'
        result = ', '.join([editors, word])
        return ('editor', result)

    def format_volume_and_series(self, e):
        volume_and_series = [
            if_next('volume'),
            optional(e, 'volume'),
            if_next('of'),
            optional(e, 'series')
        ]

        number_and_series = [
            if_next('number'),
            optional(e, 'number'),
            if_next('in'),
            optional(e, 'series')
        ]
        series = optional(e, 'series')

        if present(volume_and_series):
            return flat(volume_and_series)
        elif present(number_and_series):
            return flat(number_and_series)
        else:
            return series

    def format_chapter_and_pages(self, e):
        return flat([
            optional(e, 'chapter'),
            if_prev_and_next(','),
            optional(e, 'pages')
        ])

    def format_edition(self, e):
        return optional(e, 'edition', apply_func=lambda x: x.lower())

    def format_date(self, e):
        return [
            optional(e, 'month'),
            get(e, 'year')
        ]

    def format_title(self, e):
        def protected_capitalize(x):
            """Capitalize string, but protect {...} parts."""
            result = ""
            level = 0
            for pos, c in enumerate(x):
                if c == '{':
                    level += 1
                elif c == '}':
                    level -= 1
                elif pos == 0:
                    c = c.upper()
                elif level <= 0:
                    c = c.lower()
                result += c
            return '"%s"' % result

        return get(e, 'title', apply_func=protected_capitalize)

    def format_address_publisher_date(self, e):
        """Format address, publisher and date.
        Everything is optional, except the date.
        """
        address = optional(e, 'address')
        publisher = optional(e, 'publisher')
        date = self.format_date(e)
        if present(address):
            return [address, date, publisher]
        else:
            return [publisher, date]

    def format_url(self, e):
        return optional(e, 'url')

    def format_web_refs(self, e):
        return [
            self.format_url(e),
            self.format_doi(e)
        ]

    def format_article(self, e):
        pages = get(e, 'pages')
        volume = optional(e, 'volume')

        if present(volume):
            volume_and_pages = [
                volume,
                optional(e, 'number', apply_func=lambda x: "(%s)" % x),
                (None, ':'),
                pages
            ]
        else:
            volume_and_pages = [(None, 'pages'), pages]
        return [
            self.format_author_or_editor(e),
            self.format_title(e),
            get(e, 'journal'),
            volume_and_pages,
            self.format_date(e),
            self.format_web_refs(e),
        ]

    def format_book(self, e):
        return [
            self.format_names(e, 'author'),
            self.format_title(e),
            self.format_volume_and_series(e),
            [
                get(e, 'publisher'),
                optional(e, 'address'),
                self.format_edition(e),
                self.format_date(e)
            ],
            self.format_web_refs(e),
        ]
        return template.format_data(e)

    def format_booklet(self, e):
        return [
            self.format_names(e, 'author'),
            self.format_title(e),
            self.format_chapter_and_pages(e),
            [
                optional(e, 'howpublished'),
                optional(e, 'address'),
                self.format_date(e)
            ],
            self.format_web_refs(e),
        ]

    def format_inbook(self, e):
        return [
            self.format_names(e, 'author'),
            self.format_title(e),
            self.format_chapter_and_pages(e),
            self.format_volume_and_series(e),
            [
                get(e, 'publisher'),
                optional(e, 'address'),
                self.format_edition(e),
                self.format_date(e)
            ],
            self.format_web_refs(e)
        ]

    def format_incollection(self, e):
        return [
            self.format_names(e, 'author'),
            self.format_title(e),
            [
                ('book', 'In'),
                self.format_editor(e),
                get(e, 'booktitle'),
                self.format_volume_and_series(e),
                self.format_chapter_and_pages(e)
            ],
            [
                optional(e, 'publisher'),
                optional(e, 'address'),
                self.format_edition(e),
                self.format_date(e)
            ],
            self.format_web_refs(e),
        ]

    def format_inproceedings(self, e):
        return [
            self.format_names(e, 'author'),
            self.format_title(e),
            [
                ('book', 'In'),
                self.format_editor(e),
                get(e, 'booktitle'),
                self.format_volume_and_series(e),
                optional(e, 'pages'),
                self.format_address_publisher_date(e),
            ],
            self.format_web_refs(e),
        ]

    def format_manual(self, e):
        return [
            self.format_names(e, 'author'),
            self.format_title(e, 'title'),
            [
                optional(e, 'organization'),
                optional(e, 'address'),
                self.format_edition(e),
                self.format_date(e)
            ],
            self.format_web_refs(e),
        ]

    def format_mastersthesis(self, e):
        return [
            self.format_names(e, 'author'),
            self.format_title(e),
            [
                ('master_thesis', 'Master\'s thesis'),
                get(e, 'school'),
                optional(e, 'address'),
                self.format_date(e)
            ],
            self.format_web_refs(e),
        ]

    def format_misc(self, e):
        return [
            self.format_names(e, 'author'),
            self.format_title(e),
            optional('howpublished'),
            self.format_date(e),
            self.format_web_refs(e)
        ]

    def format_phdthesis(self, e):
        return [
            self.format_names(e, 'author'),
            self.format_title(e),
            [
                ('phd_thesis', 'PhD thesis'),
                get(e, 'school'),
                optional(e, 'address'),
                self.format_date(e)
            ],
            self.format_web_refs(e),
        ]

    def format_proceedings(self, e):
        editors = self.format_editor(e)
        if present(editors):
            template = [
                editors,
                self.format_title(e),
                self.format_volume_and_series(e),
                self.format_address_publisher_date(e),
            ]
        else:
            template = [
                optional(e, 'organization'),
                self.format_title(e),
                self.format_volume_and_series(e),
                self.format_address_publisher_date(e),
            ]

        return template + self.format_web_refs(e)

    def format_techreport(self, e):
        return [
            self.format_names(e, 'author'),
            self.format_title(e, 'title'),
            [
                optional(e, 'type'),
                (None, 'Technical Report'),
                optional(e, 'number'),
                get(e, 'institution')
            ],
            optional(e, 'address'),
            self.format_date(e),
            self.format_web_refs(e)
        ]

    def format_unpublished(self, e):
        return [
            self.format_names(e, 'author'),
            self.format_title(e),
            self.format_date(e),
            self.format_web_refs(e)
        ]

    def format_other(self, e):
        return [
            self.format_names(e.authors),
            self.format_title(e.title),
            self.format_web_refs(e)
        ]


def html(entry):
    """
    FormattedEntry
    """

    def to_html(el):
        return E.SPAN(E.CLASS(el[0]), el[1]) if el[0] is not None else E.SPAN(el[1])

    base = E.SPAN()
    for e in entry.text:
        if type(e) == tuple and e[1] is not None:
            base.append(to_html(e))
        else:
            for ee in e:
                if type(ee) == tuple and ee[1] is not None:
                    base.append(to_html(ee))

    return E.LI(E.SPAN(E.CLASS('ref'), entry.label), base)


def styling(entries, styler=IEEEStyle()):
    """
    """
    return styler.format_entries(entries)
