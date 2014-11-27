__author__ = 'christian'

from html_citation.cite import CitationSystem
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
