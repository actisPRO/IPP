from argument import Argument


class Instruction:
    def __init__(self, opcode: str, order: int):
        self.opcode = opcode
        self.order = order
        self.args = []

    def add_arg(self, arg: Argument):
        self.args.append(arg)
