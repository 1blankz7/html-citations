from pybtex.database.input import bibtex
import lxml.html as ET
import html_citation.citation_style as citation_style


class CitationSystem:
    """
    """
    def __init__(self, source_file_name, output_file_name):
        self.source_file_name = source_file_name
        self.output_file_name = output_file_name

    def run(self):
        # load file that was specified with source_file_name
        xml_tree = self.load(self.source_file_name)
        xml_root = xml_tree.getroot()
        # parse loaded file
        data = self.parse_xml(xml_root)
        # load the bibtex file
        bibdata = self.load_bibtex(data['bibliography'])

        structure = self.build_structure(bibdata, data['cites'])
        self.replace_citations(xml_root, structure)
        xml_tree.write(self.output_file_name, method='html')

    def load(self, filename):
        """Load a html/xml file in a processable format.
        """
        return ET.parse(filename)

    def parse_xml(self, xml_root):
        """Parse the file for cites.

        Method parses the file for occurences of cites and special settings.
        If no bibliography was specified, the system ends up.
        """
        cites = []
        for cite in xml_root.iter('cite'):
            cites.append(cite.text)

        bib = list(xml_root.iter('bibliography'))
        if len(bib) > 0:
            return {
                'cites': cites,
                'bibliography': bib[0].text,
                'config': bib[0].attrib
            }
        else:
            exit

    def load_bibtex(self, filename):
        #open a bibtex file
        parser = bibtex.Parser()
        return parser.parse_file(filename)

    def build_structure(self, bib, cites):
        # find cites duplicates
        entries = bib.entries
        bib = []
        sorted_cites = []
        for cite in cites:
            if cite[0] == '{' and cite[-1] == '}':
                key = cite[1:-1]
                if key not in sorted_cites:
                    bib.append(entries[key])
                    sorted_cites.append(key)
        structure = citation_style.styling(bib)

        return list(structure)

    def replace_citations(self, xml_data, structured):
        """Replaces the cites with a individual number starting from '1'.
        """
        for node in xml_data.iter('cite'):
            for e in structured:
                if node.text == ("{%s}" % e.key):
                    node.text = str(e.label)
        # build references
        bib = list(xml_data.iter('bibliography'))
        bib[0].text = ""
        for e in structured:
            bib[0].append(citation_style.html(e))

    def report(self):
        """Creates a report with some information that could be logged.
        """
        pass

    def __repr__(self):
        return "<CitationSystem(%s)>" % self.filename