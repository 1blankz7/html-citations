from pybtex.database.input import bibtex
import lxml.html as ET
import citation_style


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
        sorted_cites = {}
        structure = []
        idx = 1
        for cite in cites:
            if cite not in sorted_cites:
                sorted_cites[cite] = idx
                idx += 1

        for cite in sorted_cites:
            if cite[0] == '{' and cite[-1] == '}':
                key = cite[1:-1]
                if key in bib.entries.keys():
                    structure.append({
                        'key': key,
                        'cite': cite,
                        'entry': bib.entries[key],
                        'number': sorted_cites[cite]
                    })

        return structure

    def replace_citations(self, xml_data, structured):
        """Replaces the cites with a individual number starting from '1'.
        """
        for node in xml_data.iter('cite'):
            for entry in structured:
                if node.text == entry['cite']:
                    node.text = str(entry['number'])
                    entry['used'] = True
        # build references
        entries = [e for e in structured if e['used']]
        entries = sorted(entries, key=lambda x: x['number'])
        bib = list(xml_data.iter('bibliography'))
        bib[0].text = ""
        for e in entries:
            bib[0].append(citation_style.styling(
                e['entry'], number=e['number']))

    def report(self):
        """Creates a report with some information that could be logged.
        """
        pass

    def __repr__(self):
        return "<CitationSystem(%s)>" % self.filename


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Citation system.')
    parser.add_argument('input_filename', type=str, nargs=1,
                        help='the path of the input file')
    parser.add_argument('output_filename', type=str, nargs=1,
                        help='the path of the output file; " + \
                            "can be the same as the input file')

    args = parser.parse_args()

    input_filename = args.input_filename[0]
    output_filename = args.output_filename[0]

    cs = CitationSystem(input_filename, output_filename)
    cs.run()
