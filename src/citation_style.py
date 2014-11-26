from lxml.html import builder as E
from pybtex.style.formatting import BaseStyle
import types


def get(entry, field, apply_func=None):
    e = entry.fields[field]
    if apply_func is not None:
        e = apply_func(e)
    return (field, e)


def if_next(value):
    def f(n):
        return (None, str(value)) if present(n) else None
    return f


def optional(entry, field, apply_func=None):
    try:
        return get(entry, field, apply_func)
    except KeyError:
        return (field, None)


def present(opt):
    if type(opt) == list:
        for el in opt[:2]:
            if not isinstance(el, type.FunctionType):
                return present(el)
    elif type(opt) == tuple:
        return opt[1] is not None


def flat(opt_arr):
    text = []
    for idx in range(len(opt_arr)):
        el = opt_arr[idx]
        if isinstance(el, type.FunctionType):
            text.append(el(opt_arr[idx+1]))
        else:
            text.append(el)
    return text


class IEEEStyler(BaseStyle):
    """
    """

    def format_name(self, person):
        print(person)
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

        names = list([self.format_name(a) for a in e.persons[role]])
        
        if len(names) > 0:
            text = " and ".join(names)
            return text
        else:
            return (None, None)

    def format_author_or_editor(self, e):
        author = self.format_names(e, 'author')
        if not present(author):
            return ('editor', self.format_editor(e))
        else:
            return ('author', author)

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
        return result

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
            if_next(','),
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

    def format_address_organization_publisher_date(self, e):
        """Format address, publisher and date.
        Everything is optional, except the date.
        """
        address = optional(e, 'address')
        publisher = optional(e, 'publisher')
        date = get(e, 'date')
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
            self.format_title(e, 'title'),
            get(e, 'journal'),
            volume_and_pages,
            self.format_date(e),
            self.format_web_refs(e),
        ]

    def format_book(self, e):
        template = toplevel [
            self.format_author_or_editor(e),
            self.format_btitle(e, 'title'),
            self.format_volume_and_series(e),
            sentence [
                field('publisher'),
                optional_field('address'),
                self.format_edition(e),
                date
            ],
            sentence(capfirst=False) [ optional_field('note') ],
            self.format_web_refs(e),
        ]
        return template.format_data(e)

    def format_booklet(self, e):
        template = toplevel [
            self.format_names('author'),
            self.format_title(e, 'title'),
            sentence [
                optional_field('howpublished'),
                optional_field('address'),
                date,
                optional_field('note'),
            ],
            self.format_web_refs(e),
        ]
        return template.format_data(e)

    def format_inbook(self, e):
        template = toplevel [
            sentence [self.format_names('author')],
            sentence [
                self.format_btitle(e, 'title'),
                self.format_chapter_and_pages(e),
            ],
            self.format_volume_and_series(e),
            sentence [
                field('publisher'),
                optional_field('address'),
                optional [
                    words [field('edition'), 'edition']
                ],
                date,
                optional_field('note'),
            ],
            self.format_web_refs(e),
        ]
        return template.format_data(e)

    def format_incollection(self, e):
        template = toplevel [
            sentence [self.format_names('author')],
            self.format_title(e, 'title'),
            words [
                'In',
                sentence(capfirst=False) [
                    optional[ self.format_editor(e, as_sentence=False) ],
                    self.format_btitle(e, 'booktitle', as_sentence=False),
                    self.format_volume_and_series(e, as_sentence=False),
                    self.format_chapter_and_pages(e),
                ],
            ],
            sentence [
                optional_field('publisher'),
                optional_field('address'),
                self.format_edition(e),
                date,
            ],
            self.format_web_refs(e),
        ]
        return template.format_data(e)

    def format_inproceedings(self, e):
        template = toplevel [
            sentence [self.format_names('author')],
            self.format_title(e, 'title'),
            words [
                'In',
                sentence(capfirst=False) [
                    optional[ self.format_editor(e, as_sentence=False) ],
                    self.format_btitle(e, 'booktitle', as_sentence=False),
                    self.format_volume_and_series(e, as_sentence=False),
                    optional[ pages ],
                ],
                self.format_address_organization_publisher_date(e),
            ],
            sentence(capfirst=False) [ optional_field('note') ],
            self.format_web_refs(e),
        ]
        return template.format_data(e)

    def format_manual(self, e):
        # TODO this only corresponds to the bst style if author is non-empty
        # for empty author we should put the organization first
        template = toplevel [
            optional [ sentence [ self.format_names('author') ] ],
            self.format_btitle(e, 'title'),
            sentence [
                optional_field('organization'),
                optional_field('address'),
                self.format_edition(e),
                optional[ date ],
            ],
            sentence(capfirst=False) [ optional_field('note') ],
            self.format_web_refs(e),
        ]
        return template.format_data(e)

    def format_mastersthesis(self, e):
        template = toplevel [
            sentence [self.format_names('author')],
            self.format_title(e, 'title'),
            sentence[
                "Master's thesis",
                field('school'),
                optional_field('address'),
                date,
            ],
            sentence(capfirst=False) [ optional_field('note') ],
            self.format_web_refs(e),
        ]
        return template.format_data(e)

    def format_misc(self, e):
        template = toplevel [
            optional[ sentence [self.format_names('author')] ],
            optional[ self.format_title(e, 'title') ],
            sentence[
                optional[ field('howpublished') ],
                optional[ date ],
            ],
            sentence(capfirst=False) [ optional_field('note') ],
            self.format_web_refs(e),
        ]
        return template.format_data(e)

    def format_phdthesis(self, e):
        template = toplevel [
            sentence [self.format_names('author')],
            self.format_btitle(e, 'title'),
            sentence[
                'PhD thesis',
                field('school'),
                optional_field('address'),
                date,
            ],
            sentence(capfirst=False) [ optional_field('note') ],
            self.format_web_refs(e),
        ]
        return template.format_data(e)

    def format_proceedings(self, e):
        template = toplevel [
            first_of [
                # there are editors
                optional [
                    join(' ')[
                        self.format_editor(e),
                        sentence [
                            self.format_btitle(e, 'title', as_sentence=False),
                            self.format_volume_and_series(e, as_sentence=False),
                            self.format_address_organization_publisher_date(e),
                        ],
                    ],
                ],
                # there is no editor
                optional_field('organization'),
                sentence [
                    self.format_btitle(e, 'title', as_sentence=False),
                    self.format_volume_and_series(e, as_sentence=False),
                    self.format_address_organization_publisher_date(
                        e, include_organization=False),
                ],
            ],
            sentence(capfirst=False) [ optional_field('note') ],
            self.format_web_refs(e),
        ]
        return template.format_data(e)

    def format_techreport(self, e):
        template = toplevel [
            sentence [self.format_names('author')],
            self.format_title(e, 'title'),
            sentence [
                words[
                    first_of [
                        optional_field('type'),
                        'Technical Report',
                    ],
                    optional_field('number'),
                ],
                field('institution'),
                optional_field('address'),
                date,
            ],
            sentence(capfirst=False) [ optional_field('note') ],
            self.format_web_refs(e),
        ]
        return template.format_data(e)

    def format_unpublished(self, e):
        template = toplevel [
            sentence [self.format_names('author')],
            self.format_title(e, 'title'),
            sentence(capfirst=False) [
                field('note'),
                optional[ date ]
            ],
            self.format_web_refs(e),
        ]
        return template.format_data(e)

    def format_other(self, e):
        template = toplevel[
            self.format_names(e.authors),
            self.format_title(e.title),
            sentence(capfirst=False)[optional_field('note')],
            self.format_web_refs(e),
        ]
        return template.format_data(e)


def html(entry):
    """
    FormattedEntry
    """
    return E.LI(
        E.SPAN(E.CLASS('ref'), entry.label),
        E.SPAN(entry.text))


def styling(entries, styler=IEEEStyler()):
    """
    """
    # build structure for citation with specific formatters
    return styler.format_entries(entries)
