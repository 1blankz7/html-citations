from lxml.html import builder as E


class IEEEStyler:
    """
    """

    def format_author(self, person):
        first = person.get_part_as_text('first')
        last = person.get_part_as_text('last')

        if len(first) > 0 and len(last) > 0:
            return "%s. %s" % (first[0], last)
        elif len(last) > 0:
            return last
        else:
            return None

    def format_publish(self, publish):
        return str(publish)

    def format_url(self, url):
        return str(url)

    def format_title(self, title):
        return '"%s"' % title

    def concat_authors(self, authors):
        author_text = ""
        authors = [self.format_author(a) for a in authors]

        author_text = " and ".join(authors)
        return author_text


def styling(data, styler=IEEEStyler(), number='*'):
    """
    """
    # build structure for citation with specific formatters
    print(data.type)
    structure = {
        'ref': (0, number, ''),
        'authors': (1, styler.concat_authors(data.persons['Author']), '.'),
        'title': (2, styler.format_title(data.fields['Title']), ','),
        'year': (10, data.fields['Year'], '.')
    }
    if 'Url' in data.fields:
        structure['url'] = (7, styler.format_url(data.fields['Url']), ',')
    else:
        structure['url'] = None
    if 'Publisher' in data.fields:
        structure['publisher'] = (6, styler.format_url(
            data.fields['Publisher']), ',')
    else:
        structure['publisher'] = None
    # filter none values
    filtered = filter(lambda e: structure[e] is not None, structure)
    filtered = sorted(filtered, key=lambda e: structure[e][0])
    # concat result with comma and dot
    base = E.LI()
    for e in filtered:
        span = E.SPAN(E.CLASS(e), str(structure[e][1]) + structure[e][2])
        base.append(span)
    return base
