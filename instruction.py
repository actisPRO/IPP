from argument import Argument


class Instruction:
    def __init__(self, opcode, number):
        self.opcode = opcode
        self.number = number
        self.args = []

    def add_arg(self, arg: Argument):
        self.args.append(arg)
