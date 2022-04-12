class Variable:
    def __init__(self, var_type, value):
        self.type = var_type
        self.value = value

        if self.type == 'string' and self.value is None:
            self.value = ''

    def __str__(self):
        return f"{self.type}@{self.value}"

    def float_value(self) -> float:
        if self.type != 'float':
            raise ValueError()

        try:
            return float(self.value)
        except ValueError:
            return float.fromhex(self.value)

