"""Misc. file parsers that are useful for other parsers"""
from xml.sax import saxutils, parse, parseString

class ExcelHandler(saxutils.handler.ContentHandler):
    """

    This class is taken from the Python Cookbook so I guess the copyright
    goes to them.

    Memo: changed the handler from DefaultHandler to ContentHandler as the
    former doesn't seem to exist in Py2. (?)
    """

    def __init__(self):
        self.chars = []
        self.cells = []
        self.rows = []
        self.tables = []

    def characters(self, content):
        self.chars.append(content)

    def startElement(self, name, atts):
        if name == "Cell":
            self.chars = []
        elif name == "Row":
            self.cells = []
        elif name == "Table":
            self.rows = []

    def endElement(self, name):
        if name == "Cell":
            self.cells.append(''.join(self.chars))
        elif name == "Row":
            self.rows.append(self.cells)
        elif name == "Table":
            self.tables.append(self.rows)


def parse_excel_xml(xml_file):
    """Return a list of the tables (2D arrays) in the Excel XML file."""
    handler = ExcelHandler()
    parse(xml_file, handler)
    return handler.tables

def parse_excel_xml_string(xml_string):
    """Return a list of the tables (2D arrays) in the Excel XML file."""
    handler = ExcelHandler()
    parseString(xml_string, handler)
    return handler.tables
