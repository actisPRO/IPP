import io
import os.path
import sys
import xml.etree.ElementTree as ET

from context import Context
from exit_code import ExitCode


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

        self.context = Context()

    def parse_xml(self):
        root = self.xml_tree.getroot()

        if root.tag != 'program':
            print("ERROR: Invalid XML root.", file=sys.stderr)
            exit(ExitCode.UNEXPECTED_XML)

        self.sort_xml(root)

        print(root[0].attrib)

    @staticmethod
    def sort_xml(root):
        try:
            root[:] = sorted(root, key=lambda child: int(child.get('order')))
        except Exception as e:
            print(str(e), file=sys.stderr)
            print("Error while sorting instructions.")
            exit(ExitCode.UNEXPECTED_XML)

        for child in root:
            try:
                child[:] = sorted(child, key=lambda child: child.tag)
            except Exception as e:
                print(str(e) + "\n", file=sys.stderr)
                print("Error while sorting arguments", file=sys.stderr)
                exit(32)


