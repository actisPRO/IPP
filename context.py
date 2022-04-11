class Context:
    def __init__(self):
        self.instructions = list()
        self.current_pos = 0
        self.GF = dict()
        self.TF = None
        self.LFs = list()
        self.calls = list()
        self.labels = dict()