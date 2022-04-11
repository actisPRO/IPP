import sys

from argument import Argument
from context import Context
from exit_code import ExitCode
from variable import Variable


class Instruction:
    def __init__(self, opcode: str, order: int):
        self.opcode = opcode
        self.order = order
        self.args = []

    def add_arg(self, arg: Argument):
        self.args.append(arg)

    def error(self, message):
        print(f'ERROR (instruction #{self.order}): {message}', file=sys.stderr)

    def execute(self, ctx: Context):
        if self.opcode == 'MOVE':
            self.move(ctx)
        elif self.opcode == 'CREATEFRAME':
            self.createframe(ctx)
        elif self.opcode == 'PUSHFRAME':
            self.pushframe(ctx)
        elif self.opcode == 'POPFRAME':
            self.popframe(ctx)
        elif self.opcode == 'DEFVAR':
            self.defvar(ctx)
        elif self.opcode == 'CALL':
            self.call(ctx)
        elif self.opcode == 'RETURN':
            self.exec_return(ctx)

    def move(self, ctx: Context):
        return

    def createframe(self, ctx: Context):
        return

    def pushframe(self, ctx: Context):
        return

    def popframe(self, ctx: Context):
        return

    def defvar(self, ctx: Context):
        data = self.args[0].value.split('@')


        return

    def call(self, ctx: Context):
        return

    def exec_return(self, ctx: Context):
        return
