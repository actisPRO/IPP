import sys

from exit_code import ExitCode
from variable import Variable
from argument import Argument


class Context:
    instructions = list()
    GF = dict()
    LFs = list()
    labels = dict()
    calls = list()
    stack = list()

    def __init__(self, input_stream):
        self.current_pos = 0
        self.TF = None
        self.input = input_stream

    def execute(self):
        while self.current_pos != len(self.instructions):
            self.instructions[self.current_pos].execute(self)
            self.current_pos += 1

    def load_labels(self):
        for i in self.instructions:
            if i.opcode == 'LABEL':
                self.labels[i.args[0].value] = int(i.order)

    def error(self, message):
        print(f'ERROR (instruction #{self.current_pos + 1}): {message}', file=sys.stderr)

    def get_variable(self, frame: str, name: str) -> Variable:
        if frame == 'GF':
            if name not in self.GF.keys():
                self.error(f'variable {name} is not defined in the global frame.')
                exit(ExitCode.UNDEFINED_VARIABLE.value)

            if self.GF[name].type is None:
                self.error(f'variable {name} is declared but undefined.')
                exit(ExitCode.MISSING_VALUE.value)

            return self.GF[name]
        elif frame == 'LF':
            if len(self.LFs) == 0:
                self.error('local frame does not exist.')
                exit(ExitCode.UNDEFINED_FRAME.value)

            if name not in self.LFs[-1].keys():
                self.error(f'variable {name} is not defined in the local frame.')
                exit(ExitCode.SEMANTIC_ERROR.value)

            if self.LFs[-1][name].type is None:
                self.error(f'variable {name} is declared but undefined.')
                exit(ExitCode.MISSING_VALUE.value)

            return self.LFs[-1][name]
        elif frame == 'TF':
            if self.TF is None:
                self.error(f'temporary frame is not defined.')
                exit(ExitCode.UNDEFINED_FRAME.value)

            if name not in self.TF.keys():
                self.error(f'variable {name} is not defined in the temporary frame.')
                exit(ExitCode.SEMANTIC_ERROR.value)

            if self.TF[name].type is None:
                self.error(f'variable {name} is declared but is not defined.')
                exit(ExitCode.MISSING_VALUE.value)

            return self.TF[name]

    def get_variable_from_arg(self, arg: Argument) -> Variable:
        var = Variable(None, None)
        if arg.type == 'var':
            sym_data = arg.value.split('@')
            sym = self.get_variable(sym_data[0], sym_data[1])
            var.type = sym.type
            var.value = sym.value
        else:
            var.type = arg.type
            var.value = arg.value

        return var


    def def_var(self, frame: str, name: str):
        var = Variable(None, None)

        if frame == 'GF':
            if name in self.GF.keys():
                self.error(f'variable {name} is already defined in the global frame.')
                exit(ExitCode.SEMANTIC_ERROR.value)
            self.GF[name] = var
        elif frame == 'LF':
            if len(self.LFs) == 0:
                self.error('local frame does not exist.')
                exit(ExitCode.UNDEFINED_FRAME.value)

            if name in self.LFs[-1].keys():
                self.error(f'variable {name} is already defined in the local frame.')
                exit(ExitCode.SEMANTIC_ERROR.value)

            self.LFs[-1][name] = var
        elif frame == 'TF':
            if self.TF is None:
                self.error(f'temporary frame is not defined.')
                exit(ExitCode.UNDEFINED_FRAME.value)

            if name in self.TF.keys():
                self.error(f'variable {name} is already defined in the temporary frame.')
                exit(ExitCode.SEMANTIC_ERROR.value)

            self.TF[name] = var

    def set_variable(self, frame: str, name: str, var_type, value):
        var = Variable(var_type, value)

        if frame == 'GF':
            if name not in self.GF.keys():
                self.error(f'variable {name} is not defined in the global frame.')
                exit(ExitCode.SEMANTIC_ERROR.value)

            self.GF[name] = var
        elif frame == 'LF':
            if len(self.LFs) == 0:
                self.error('local frame does not exist.')
                exit(ExitCode.UNDEFINED_FRAME.value)

            if name not in self.LFs[-1].keys():
                self.error(f'variable {name} is not defined in the local frame.')
                exit(ExitCode.SEMANTIC_ERROR.value)

            self.LFs[-1][name] = var
        elif frame == 'TF':
            if self.TF is None:
                self.error(f'temporary frame is not defined.')
                exit(ExitCode.UNDEFINED_FRAME.value)

            if name not in self.TF.keys():
                self.error(f'variable {name} is not defined in the temporary frame.')
                exit(ExitCode.SEMANTIC_ERROR.value)

            self.TF[name] = var

    def jump_to_label(self, label: str):
        if label not in self.labels.keys():
            self.error(f'label {label} does not exist.')
            exit(ExitCode.SEMANTIC_ERROR.value)

        self.current_pos = self.labels[label] - 1
