import argparse
import sys

from exit_code import ExitCode
from interpreter import Interpreter

if __name__ == '__main__':
    parser = argparse.ArgumentParser('interpret.py', add_help=False)
    parser.add_argument('--help', action='help', help='show this help message and exit.')
    parser.add_argument('--source', action='store', help='set an input XML file.')
    parser.add_argument('--input', action='store', help='set input for the interpretation.')

    args = parser.parse_args()
    if args.source is None and args.input is None:
        Interpreter.error('at least one argument (--source or --input) must be set.')
        exit(ExitCode.MISSING_ARGUMENT.value)

    try:
        interpreter = Interpreter(args.source, args.input)
        interpreter.parse_xml()
        interpreter.execute()
    except FileNotFoundError:
        Interpreter.error("specified file was not found.")
        exit(ExitCode.READ_ERROR.value)
    except Exception as e:
        Interpreter.error(f"Unexpected error:\n{e}")
        exit(ExitCode.INTERNAL_ERROR.value)

