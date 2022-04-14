import sys


class Stats:
    def __init__(self):
        self.insts = 0
        self.hot = dict()
        self.vars = 0

    def calc_hot(self) -> int:
        instructions = dict()

        for key in self.hot.keys():
            if key[0] not in instructions.keys():
                instructions[key[0]] = 0
            instructions[key[0]] += self.hot[key]

        max_val = max(instructions, key=instructions.get)
        min_order = sys.maxsize
        for key in self.hot.keys():
            if key[0] == max_val and key[1] < min_order:
                min_order = key[1]

        return min_order
