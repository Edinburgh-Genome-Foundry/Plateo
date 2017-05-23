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


def parse_excel_xml(xml_file=None, xml_string=None):
    """Return a list of the tables (2D arrays) in the Excel XML.

    Provide either the path to an XML file, or a string of XML content.
    """
    handler = ExcelHandler()
    if xml_file is not None:
        parse(xml_file, handler)
    elif xml_string is not None:
        parseString(xml_string, handler)
    else:
        raise ValueError("At least one of xml_file or xml_string should be"
                         " provided.")
    return handler.tables
