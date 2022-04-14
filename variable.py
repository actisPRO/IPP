class Variable:
    def __init__(self, var_type, value):
        self.type = var_type
        self.value = value

        if self.type == 'string' and self.value is None:
            self.value = ''
        elif self.type == 'bool' and type(self.value) is bool:
            if self.value:
                self.value = 'true'
            else:
                self.value = 'false'

    def __str__(self):
        return f"{self.type}@{self.value}"

    def unwrap(self):
        if self.type == 'int':
            return int(self.value)
        elif self.type == 'float':
            return self.float_value()
        elif self.type == 'bool':
            return self.value.lower() == 'true'
        elif self.type == 'string':
            return self.value
        else:
            return None

    def float_value(self) -> float:
        if self.type != 'float' and self.type != 'int':
            raise ValueError()

        try:
            return float(self.value)
        except ValueError:
            return float.fromhex(self.value)

