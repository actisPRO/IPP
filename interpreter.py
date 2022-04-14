import io
import os.path
import re
import sys
import xml.etree.ElementTree as ET

from context import Context
from instruction import Instruction
from argument import Argument
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

        try:
            self.xml_tree = ET.parse(xml)
        except ET.ParseError:
            self.error('Invalid XML file.')
            exit(ExitCode.BAD_XML.value)

        if input_file is None:
            self.input_stream = sys.stdin
        else:
            if not os.path.exists(input_file):
                raise FileNotFoundError
            else:
                self.input_stream = io.open(input_file, 'r')

        self.context = Context(self.input_stream)

    def execute(self):
        self.context.execute()

    @staticmethod
    def error(message: str):
        print(f'ERROR: {message}', file=sys.stderr)

    def parse_xml(self):
        root = self.xml_tree.getroot()

        self.sort_xml(root)
        self.validate_xml(root)
        self.load_instructions(root)
        self.context.load_labels()

    def load_instructions(self, root: ET.Element):
        for child in root:
            instruction = Instruction(
                child.attrib['opcode'].upper(),
                int(child.attrib['order']))
            for arg in child:
                instruction.add_arg(Argument(
                    arg.attrib['type'].lower(),
                    arg.text
                ))

            self.context.instructions.append(instruction)

    @staticmethod
    def sort_xml(root: ET.Element):
        try:
            root[:] = sorted(root, key=lambda child: int(child.get('order')))
        except Exception as e:
            print(str(e), file=sys.stderr)
            print("Unexpected error while sorting instructions.")
            exit(ExitCode.UNEXPECTED_XML_STRUCTURE.value)

        for child in root:
            try:
                child[:] = sorted(child, key=lambda child: child.tag)
            except Exception as e:
                print(str(e) + "\n", file=sys.stderr)
                print("Unexpected error while sorting arguments", file=sys.stderr)
                exit(ExitCode.UNEXPECTED_XML_STRUCTURE.value)

    @staticmethod
    def validate_xml(root: ET.Element):
        if root.tag != 'program':
            print(f"ERROR: Expected {root.tag} to be program.", file=sys.stderr)
            exit(ExitCode.UNEXPECTED_XML_STRUCTURE.value)

        if root.attrib['language'] is None or root.attrib['language'].lower() != 'ippcode22':
            print(f'ERROR: Expected root to containt attribute language with value "IPPcode22".', file=sys.stderr)
            exit(ExitCode.UNEXPECTED_XML_STRUCTURE.value)

        expected_order = 0
        for child in root:
            if child.tag != 'instruction':
                print(f'ERROR: Unexpected XML-tag {child.tag}. Expected: instruction', file=sys.stderr)
                exit(ExitCode.UNEXPECTED_XML_STRUCTURE.value)

            attributes = list(child.attrib.keys())
            if not ('order' in attributes) or not ('opcode' in attributes):
                print('ERROR: Every instruction should contain opcode and order atrtibutes.', file=sys.stderr)
                exit(ExitCode.UNEXPECTED_XML_STRUCTURE.value)

            if int(child.attrib['order']) <= expected_order:
                print(f'ERROR: Expected order to be bigger then {expected_order} but it was {child.attrib["order"]}.',
                      file=sys.stderr)
                exit(ExitCode.UNEXPECTED_XML_STRUCTURE.value)

            arg1 = False
            arg2 = False
            arg3 = False
            for arg in child:
                if arg.tag == 'arg1':
                    arg1 = True
                elif arg.tag == 'arg2':
                    arg2 = True
                elif arg.tag == 'arg3':
                    arg3 = True
                else:
                    Interpreter.error(f'ERROR: Expected {arg.tag} to be arg1, arg2 or arg3.')
                    exit(ExitCode.UNEXPECTED_XML_STRUCTURE.value)

                arg_attrs = list(arg.attrib)
                if not ('type' in arg_attrs):
                    Interpreter.error(f'ERROR: {arg.tag} of instruction #{child.attrib["order"]} does not contain type info.')
                    exit(ExitCode.UNEXPECTED_XML_STRUCTURE.value)

            if (arg2 and not arg1) or (arg3 and not arg2) or (arg3 and not arg1):
                Interpreter.error('missing argument: found arg2 and arg1 does not exist, or found arg3 and arg2 or arg1 does not exist.')
                exit(ExitCode.UNEXPECTED_XML_STRUCTURE.value)

            expected_order = int(child.attrib['order'])
