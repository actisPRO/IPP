class Variable:
    def __init__(self, var_type, value):
        self.type = var_type
        self.value = value

    def __str__(self):
        return f"{self.type}@{self.value}"
