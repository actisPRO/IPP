from instruction import Instruction
from exit_code import ExitCode

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

    def get_variable(self, frame: str, name: str, caller: Instruction):
        if frame == 'GF':
            if name not in self.GF.keys():
                caller.error(f'variable {name} is not defined in the global frame.')
                exit(ExitCode.UNDEFINED_VARIABLE.value)

            return self.GF[name]
        elif frame == 'LF':
            if len(self.LFs) == 0:
                caller.error('local frame does not exist.')
                exit(ExitCode.UNDEFINED_FRAME.value)

            if name not in self.LFs[-1].keys():
                caller.error(f'variable {name} is not defined in the local frame.')
                exit(ExitCode.SEMANTIC_ERROR.value)

            return self.LFs[-1][name]
        elif frame == 'TF':
            if self.TF is None:
                caller.error(f'temporary frame is not defined.')
                exit(ExitCode.UNDEFINED_FRAME.value)

            if name not in self.TF.keys():
                caller.error(f'variable {name} is not defined in the temporary frame.')
                exit(ExitCode.SEMANTIC_ERROR.value)

            return self.TF[name]
