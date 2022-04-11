class Context:
    instructions = list()
    GF = dict()
    LFs = list()
    labels = dict()

    def __init__(self):
        self.current_pos = 0
        self.TF = None
