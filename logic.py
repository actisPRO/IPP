from enum import Enum


class LogicType(Enum):
    LT = 0
    GT = 1
    EQ = 2
    AND = 3
    OR = 4
    NOT = 5


class LogicEvaluator:
    def __init__(self, ot: LogicType, value1, value2=None):
        self.v1 = value1
        self.v2 = value2
        self.type = ot

    def eval(self) -> bool:
        funcs = {
            LogicType.LT: lambda a, b: a < b,
            LogicType.GT: lambda a, b: a > b,
            LogicType.EQ: lambda a, b: a == b,
            LogicType.AND: lambda a, b: a and b,
            LogicType.OR: lambda a, b: a or b,
            LogicType.NOT: lambda a, _: not a
        }

        return funcs[self.type](self.v1, self.v2)
