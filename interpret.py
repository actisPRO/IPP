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
        print('ERROR: at least one argument (--source or --input) must be set.', file=sys.stderr)
        exit(ExitCode.MISSING_ARGUMENT.value)

    try:
        interpreter = Interpreter(args.source, args.input)
    except FileNotFoundError:
        print('ERROR: specified file was not found.', file=sys.stderr)
        exit(ExitCode.READ_ERROR.value)