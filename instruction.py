from argument import Argument
from context import Context
from exit_code import ExitCode
from variable import Variable

class Instruction:
    def __init__(self, opcode: str, order: int):
        self.opcode = opcode
        self.order = order
        self.args = []

    def add_arg(self, arg: Argument):
        self.args.append(arg)

    def execute(self, ctx: Context):
        if self.opcode == "MOVE":
            self.move(ctx)
        elif self.opcode == "CREATEFRAME":
            self.createframe(ctx)
        elif self.opcode == "PUSHFRAME":
            self.pushframe(ctx)
        elif self.opcode == "POPFRAME":
            self.popframe(ctx)
        elif self.opcode == "DEFVAR":
            self.defvar(ctx)
        elif self.opcode == "CALL":
            self.call(ctx)
        elif self.opcode == "RETURN":
            self.exec_return(ctx)
        elif self.opcode == "PUSHS":
            self.pushs(ctx)
        elif self.opcode == "POPS":
            self.pops(ctx)
        elif self.opcode == "ADD":
            self.add(ctx)
        elif self.opcode == "SUB":
            self.sub(ctx)
        elif self.opcode == "MUL":
            self.mul(ctx)
        elif self.opcode == "IDIV":
            self.idiv(ctx)
        elif self.opcode == "LT":
            self.lt(ctx)
        elif self.opcode == "GT":
            self.gt(ctx)
        elif self.opcode == "EQ":
            self.eq(ctx)
        elif self.opcode == "AND":
            self.exec_and(ctx)
        elif self.opcode == "OR":
            self.exec_or(ctx)
        elif self.opcode == "NOT":
            self.exec_not(ctx)
        elif self.opcode == "INT2CHAR":
            self.int2char(ctx)
        elif self.opcode == "STRI2INT":
            self.stri2int(ctx)
        elif self.opcode == "READ":
            self.read(ctx)
        elif self.opcode == "WRITE":
            self.write(ctx)
        elif self.opcode == "CONCAT":
            self.concat(ctx)
        elif self.opcode == "STRLEN":
            self.strlen(ctx)
        elif self.opcode == "GETCHAR":
            self.getchar(ctx)
        elif self.opcode == "SETCHAR":
            self.setchar(ctx)
        elif self.opcode == "TYPE":
            self.type(ctx)
        elif self.opcode == "LABEL":
            self.label(ctx)
        elif self.opcode == "JUMP":
            self.jump(ctx)
        elif self.opcode == "JUMPIFEQ":
            self.jumpifeq(ctx)
        elif self.opcode == "JUMPIFNEQ":
            self.jumpifneq(ctx)
        elif self.opcode == "EXIT":
            self.exit(ctx)
        elif self.opcode == "DPRINT":
            self.dprint(ctx)
        elif self.opcode == "BREAK":
            self.exec_break(ctx)

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
        ctx.TF = dict()
        return

    def pushframe(self, ctx: Context):
        if ctx.TF is None:
            ctx.error('temporary frame is not defined.')
            exit(ExitCode.UNDEFINED_FRAME.value)

        ctx.LFs.append(ctx.TF)
        ctx.TF = None
        return

    def popframe(self, ctx: Context):
        if len(ctx.LFs) == 0:
            ctx.error('local frame stack is empty.')
            exit(ExitCode.MISSING_VALUE.value)

        ctx.TF = ctx.LFs.pop()
        return

    def defvar(self, ctx: Context):
        data = self.args[0].value.split('@')
        ctx.def_var(data[0], data[1])
        return

    def call(self, ctx: Context):
        ctx.calls.append(self.order)
        ctx.jump_to_label(self.args[0].value)
        return

    def exec_return(self, ctx: Context):
        if len(ctx.calls) == 0:
            ctx.error('call frame is empty.')
            exit(ExitCode.MISSING_VALUE.value)

        ctx.current_pos = ctx.calls.pop()
        return

    def pushs(self, ctx: Context):
        var = Variable(None, None)
        if self.args[0].type == 'var':
            sym_data = self.args[0].value.split('@')
            sym = ctx.get_variable(sym_data[0], sym_data[1])
            var.type = sym.type
            var.value = sym.value
        else:
            var.type = self.args[0].type
            var.value = self.args[0].value

        ctx.stack.append(var)
        return

    def pops(self, ctx: Context):
        return

    def add(self, ctx: Context):
        return

    def sub(self, ctx: Context):
        return

    def mul(self, ctx: Context):
        return

    def idiv(self, ctx: Context):
        return

    def lt(self, ctx: Context):
        return

    def gt(self, ctx: Context):
        return

    def eq(self, ctx: Context):
        return

    def exec_and(self, ctx: Context):
        return

    def exec_or(self, ctx: Context):
        return

    def exec_not(self, ctx: Context):
        return

    def int2char(self, ctx: Context):
        return

    def stri2int(self, ctx: Context):
        return

    def read(self, ctx: Context):
        return

    def write(self, ctx: Context):
        return

    def concat(self, ctx: Context):
        return

    def strlen(self, ctx: Context):
        return

    def getchar(self, ctx: Context):
        return

    def setchar(self, ctx: Context):
        return

    def type(self, ctx: Context):
        return

    def label(self, ctx: Context):
        return

    def jump(self, ctx: Context):
        return

    def jumpifeq(self, ctx: Context):
        return

    def jumpifneq(self, ctx: Context):
        return

    def exit(self, ctx: Context):
        return

    def dprint(self, ctx: Context):
        return

    def exec_break(self, ctx: Context):
        return
