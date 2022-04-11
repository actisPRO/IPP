import sys

from exit_code import ExitCode
from variable import Variable


class Context:
    instructions = list()
    GF = dict()
    LFs = list()
    labels = dict()

    def __init__(self):
        self.current_pos = 0
        self.TF = None

    def execute(self):
        while self.current_pos != len(self.instructions):
            self.instructions[self.current_pos].execute(self)
            self.current_pos += 1

    def load_labels(self):
        for i in self.instructions:
            if i.opcode == 'LABEL':
                self.labels[i.args[0].value] = i.order

    def error(self, message):
        print(f'ERROR (instruction #{self.current_pos + 1}): {message}', file=sys.stderr)

    def get_variable(self, frame: str, name: str):
        if frame == 'GF':
            if name not in self.GF.keys():
                self.error(f'variable {name} is not defined in the global frame.')
                exit(ExitCode.UNDEFINED_VARIABLE.value)

            return self.GF[name]
        elif frame == 'LF':
            if len(self.LFs) == 0:
                self.error('local frame does not exist.')
                exit(ExitCode.UNDEFINED_FRAME.value)

            if name not in self.LFs[-1].keys():
                self.error(f'variable {name} is not defined in the local frame.')
                exit(ExitCode.SEMANTIC_ERROR.value)

            return self.LFs[-1][name]
        elif frame == 'TF':
            if self.TF is None:
                self.error(f'temporary frame is not defined.')
                exit(ExitCode.UNDEFINED_FRAME.value)

            if name not in self.TF.keys():
                self.error(f'variable {name} is not defined in the temporary frame.')
                exit(ExitCode.SEMANTIC_ERROR.value)

            return self.TF[name]

    def set_variable(self, frame: str, name: str, var_type, value):
        var = Variable(var_type, value)

        if frame == 'GF':
            self.GF[name] = var
        elif frame == 'LF':
            if len(self.LFs) == 0:
                self.error('local frame does not exist.')
                exit(ExitCode.UNDEFINED_FRAME.value)

            self.LFs[-1][name] = var
        elif frame == 'TF':
            if self.TF is None:
                self.error(f'temporary frame is not defined.')
                exit(ExitCode.UNDEFINED_FRAME.value)

            self.TF[name] = var
