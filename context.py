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
