from argument import Argument
from context import Context


class Instruction:
    def __init__(self, opcode: str, order: int):
        self.opcode = opcode
        self.order = order
        self.args = []

    def execute(self, ctx: Context):
        print('exec')

    def add_arg(self, arg: Argument):
        self.args.append(arg)
