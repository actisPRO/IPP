import io
import os.path
import sys
import xml.etree.ElementTree as ET


class Interpreter:
    xml_tree = None
    input_stream = None
    context = None

    @staticmethod
    def __read_source_from_stdin():
        result = ''
        for line in sys.stdin:
            result += line

        return result

    def __init__(self, source_file, input_file):
        if source_file is None:
            xml = self.__read_source_from_stdin()
        else:
            xml = source_file
        self.xml_tree = ET.parse(xml)

        if input_file is None:
            self.input_stream = sys.stdin
        else:
            if not os.path.exists(input_file):
                raise FileNotFoundError
            else:
                self.input_stream = io.open(input_file, 'r')

    def parse_xml(self):
        root = self.xml_tree.getroot()
        # todo: xml validation


