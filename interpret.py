import argparse

from exit_code import ExitCode
from interpreter import Interpreter

if __name__ == '__main__':
    parser = argparse.ArgumentParser('interpret.py', add_help=False)
    parser.add_argument('--help', action='help', help='show this help message and exit.')
    parser.add_argument('--source', action='store', help='set an input XML file.')
    parser.add_argument('--input', action='store', help='set input for the interpretation.')
    parser.add_argument('--stats', action='store', help='set a stats output file.')
    parser.add_argument('--insts', action='append_const', const='insts', dest='stats_order', help='will print the amount of the executed instructions to the stats file')
    parser.add_argument('--hot', action='append_const', const='hot', dest='stats_order', help='will print the order attribute value of the most frequent instruction to the stats file')
    parser.add_argument('--vars', action='append_const', const='var', dest='stats_order', help='will print the maximum amount of initialized variables in all frames to the stats file')

    args = parser.parse_args()
    if args.source is None and args.input is None:
        Interpreter.error('at least one argument (--source or --input) must be set.')
        exit(ExitCode.MISSING_ARGUMENT.value)
    if args.stats is None and args.stats_order is not None:
        Interpreter.error('path to the stats file was not set.')
        exit(ExitCode.MISSING_ARGUMENT.value)

    try:
        interpreter = Interpreter(args.source, args.input)
        interpreter.parse_xml()
        interpreter.execute()
    except FileNotFoundError:
        Interpreter.error("specified file was not found.")
        exit(ExitCode.READ_ERROR.value)
    except Exception as e:
        Interpreter.error(f"Unexpected error of type {type(e)}:\n{e}")
        exit(ExitCode.INTERNAL_ERROR.value)

