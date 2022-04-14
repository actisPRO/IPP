from enum import Enum


class ArithmeticsType(Enum):
    ADD = 0
    SUB = 1
    MUL = 2
    IDIV = 3
    DIV = 4


class ArithmeticEvaluator:
    def __init__(self, value1: int or float, value2: int or float, ot: ArithmeticsType):
        self.v1 = value1
        self.v2 = value2
        self.type = ot

    def eval(self) -> int or float:
        funcs = {
            ArithmeticsType.ADD: lambda a, b: a + b,
            ArithmeticsType.SUB: lambda a, b: a - b,
            ArithmeticsType.IDIV: lambda a, b: a // b,
            ArithmeticsType.MUL: lambda a, b: a * b,
            ArithmeticsType.DIV: lambda a, b: a / b
        }

        return funcs[self.type](self.v1, self.v2)
