from argument import Argument
from context import Context


class Instruction:
    def __init__(self, opcode: str, order: int):
        self.opcode = opcode
        self.order = order
        self.args = []

    def add_arg(self, arg: Argument):
        self.args.append(arg)

    def execute(self, ctx: Context):
        if self.opcode == 'MOVE':
            self.move(ctx)
        elif self.opcode == 'CREATEFRAME':
            self.createframe(ctx)
        elif self.opcode == 'PUSHFRAME':
            self.pushframe(ctx)
        elif self.opcode == 'POPFRAME':
            self.popframe(ctx)
        elif self.opcode == 'DEFVAR':
            self.defvar(ctx)
        elif self.opcode == 'CALL':
            self.call(ctx)
        elif self.opcode == 'RETURN':
            self.exec_return(ctx)

    def move(self, ctx: Context):
        var_type = None
        value = None
        if self.args[1].type == 'var':
            sym_data = self.args[1].value.split('@')
            sym = ctx.get_variable(sym_data[0], sym_data[1])
            var_type = sym.type
            value = sym.value
        else:
            var_type = self.args[1].type
            value = self.args[1].value

        var_data = self.args[0].value.split('@')
        ctx.set_variable(var_data[0], var_data[1], var_type, value)

        return

    def createframe(self, ctx: Context):
        return

    def pushframe(self, ctx: Context):
        return

    def popframe(self, ctx: Context):
        return

    def defvar(self, ctx: Context):
        data = self.args[0].value.split('@')
        ctx.def_var(data[0], data[1])
        return

    def call(self, ctx: Context):
        return

    def exec_return(self, ctx: Context):
        return
