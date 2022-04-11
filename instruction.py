import sys

from argument import Argument
from context import Context
from exit_code import ExitCode


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
        elif self.opcode == 'INT2FLOAT':
            self.int2float(ctx)
        elif self.opcode == 'FLOAT2INT':
            self.float2int(ctx)
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
        sym = ctx.get_variable_from_arg(self.args[1])

        var_data = self.args[0].value.split('@')
        ctx.set_variable(var_data[0], var_data[1], sym.type, sym.value)

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
        var = ctx.get_variable_from_arg(self.args[0])
        ctx.stack.append(var)
        return

    def pops(self, ctx: Context):
        if len(ctx.stack) == 0:
            ctx.error('Stack is empty.')
            exit(ExitCode.MISSING_VALUE.value)

        var = ctx.stack.pop()

        var_data = self.args[0].value.split('@')
        ctx.set_variable(var_data[0], var_data[1], var.type, var.value)

        return

    def int2float(self, ctx: Context):
        return

    def float2int(self, ctx: Context):
        return

    def add(self, ctx: Context):
        sym1 = ctx.get_variable_from_arg(self.args[1])
        sym2 = ctx.get_variable_from_arg(self.args[2])
        if sym1.type != 'int' or sym2.type != 'int':
            ctx.error('ADD accepts only integer parameters.')
            exit(ExitCode.BAD_OPERAND_TYPE.value)

        result = int(sym1.value) + int(sym2.value)

        var = self.args[0].value.split('@')
        ctx.set_variable(var[0], var[1], 'int', result)

        return

    def sub(self, ctx: Context):
        sym1 = ctx.get_variable_from_arg(self.args[1])
        sym2 = ctx.get_variable_from_arg(self.args[2])
        if sym1.type != 'int' or sym2.type != 'int':
            ctx.error('SUB accepts only integer parameters.')
            exit(ExitCode.BAD_OPERAND_TYPE.value)

        result = int(sym1.value) - int(sym2.value)

        var = self.args[0].value.split('@')
        ctx.set_variable(var[0], var[1], 'int', result)
        return

    def mul(self, ctx: Context):
        sym1 = ctx.get_variable_from_arg(self.args[1])
        sym2 = ctx.get_variable_from_arg(self.args[2])
        if sym1.type != 'int' or sym2.type != 'int':
            ctx.error('MUL accepts only integer parameters.')
            exit(ExitCode.BAD_OPERAND_TYPE.value)

        result = int(sym1.value) * int(sym2.value)

        var = self.args[0].value.split('@')
        ctx.set_variable(var[0], var[1], 'int', result)
        return

    def idiv(self, ctx: Context):
        sym1 = ctx.get_variable_from_arg(self.args[1])
        sym2 = ctx.get_variable_from_arg(self.args[2])
        if sym1.type != 'int' or sym2.type != 'int':
            ctx.error('SUB accepts only integer parameters.')
            exit(ExitCode.BAD_OPERAND_TYPE.value)
        if int(sym2.value) == 0:
            ctx.error('Can\'t divde by zero.')
            exit(ExitCode.BAD_OPERAND_VALUE.value)

        result = int(sym1.value) // int(sym2.value)

        var = self.args[0].value.split('@')
        ctx.set_variable(var[0], var[1], 'int', result)
        return

    def lt(self, ctx: Context):
        sym1 = ctx.get_variable_from_arg(self.args[1])
        sym2 = ctx.get_variable_from_arg(self.args[2])
        if sym1.type != sym2.type:
            ctx.error('LT only accepts parameters with equal types.')
            exit(ExitCode.BAD_OPERAND_TYPE.value)

        result = False
        if sym1.type == 'int':
            result = int(sym1.value) < int(sym2.value)
        elif sym1.type == 'bool':
            if sym1.value == 'false' and sym2.value == 'true':
                result = True
            else:
                result = False
        elif sym1.type == 'string':
            result = sym1.value < sym2.value

        result = str(result).lower()

        var = self.args[0].value.split('@')
        ctx.set_variable(var[0], var[1], 'bool', result)
        return

    def gt(self, ctx: Context):
        sym1 = ctx.get_variable_from_arg(self.args[1])
        sym2 = ctx.get_variable_from_arg(self.args[2])
        if sym1.type != sym2.type:
            ctx.error('GT only accepts parameters with equal types.')
            exit(ExitCode.BAD_OPERAND_TYPE.value)

        result = False
        if sym1.type == 'int':
            result = int(sym1.value) > int(sym2.value)
        elif sym1.type == 'bool':
            if sym1.value == 'true' and sym2.value == 'false':
                result = True
            else:
                result = False
        elif sym1.type == 'string':
            result = sym1.value > sym2.value

        result = str(result).lower()

        var = self.args[0].value.split('@')
        ctx.set_variable(var[0], var[1], 'bool', result)
        return

    def eq(self, ctx: Context):
        sym1 = ctx.get_variable_from_arg(self.args[1])
        sym2 = ctx.get_variable_from_arg(self.args[2])

        if sym1.type == 'nil' or sym2.type == 'nil':
            var = self.args[0].value.split('@')
            if sym1.type == 'nil' and sym2.type != 'nil' or sym1.type != 'nil' and sym2.type == 'nil':
                ctx.set_variable(var[0], var[1], 'bool', 'false')
            else:
                ctx.set_variable(var[0], var[1], 'bool', 'true')
            return

        if sym1.type != sym2.type:
            ctx.error('EQ only accepts parameters with equal types.')
            exit(ExitCode.BAD_OPERAND_TYPE.value)

        result = False
        if sym1.type == 'int':
            result = int(sym1.value) == int(sym2.value)
        else:
            result = sym1.value == sym2.value

        result = str(result).lower()

        var = self.args[0].value.split('@')
        ctx.set_variable(var[0], var[1], 'bool', result)
        return

    def exec_and(self, ctx: Context):
        sym1 = ctx.get_variable_from_arg(self.args[1])
        sym2 = ctx.get_variable_from_arg(self.args[2])
        if sym1.type != 'bool' or sym2.type != 'bool':
            ctx.error('AND accepts only boolean parameters.')
            exit(ExitCode.BAD_OPERAND_TYPE.value)

        result = sym1.value == 'true' and sym2.value == 'true'
        result = str(result).lower()

        var = self.args[0].value.split('@')
        ctx.set_variable(var[0], var[1], 'bool', result)
        return

    def exec_or(self, ctx: Context):
        sym1 = ctx.get_variable_from_arg(self.args[1])
        sym2 = ctx.get_variable_from_arg(self.args[2])
        if sym1.type != 'bool' or sym2.type != 'bool':
            ctx.error('OR accepts only boolean parameters.')
            exit(ExitCode.BAD_OPERAND_TYPE.value)

        result = sym1.value == 'true' or sym2.value == 'true'
        result = str(result).lower()

        var = self.args[0].value.split('@')
        ctx.set_variable(var[0], var[1], 'bool', result)
        return

    def exec_not(self, ctx: Context):
        sym1 = ctx.get_variable_from_arg(self.args[1])
        if sym1.type != 'bool':
            ctx.error('NOT accepts only a boolean parameter.')
            exit(ExitCode.BAD_OPERAND_TYPE.value)

        result = sym1.value != 'true'
        result = str(result).lower()

        var = self.args[0].value.split('@')
        ctx.set_variable(var[0], var[1], 'bool', result)
        return

    def int2char(self, ctx: Context):
        sym1 = ctx.get_variable_from_arg(self.args[1])
        if sym1.type != 'int':
            ctx.error('INT2CHAR accepts only an integer parameter.')
            exit(ExitCode.BAD_OPERAND_TYPE.value)

        try:
            result = chr(int(sym1.value))
            var = self.args[0].value.split('@')
            ctx.set_variable(var[0], var[1], 'string', result)
        except ValueError:
            ctx.error(f'{sym1.value} is an incorrect Unicode code.')
            exit(ExitCode.BAD_STRING.value)

    def stri2int(self, ctx: Context):
        sym1 = ctx.get_variable_from_arg(self.args[1])
        sym2 = ctx.get_variable_from_arg(self.args[2])
        if sym1.type != 'string' or sym2.type != 'int':
            ctx.error('STRI2INT valid signature is VAR STRING INT.')
            exit(ExitCode.BAD_OPERAND_TYPE.value)
        if int(sym2.value) < 0 or int(sym2.value) >= len(sym1.value):
            ctx.error('index is out of range.')
            exit(ExitCode.BAD_STRING.value)

        char = sym1.value[int(sym2.value)]
        var = self.args[0].value.split('@')
        ctx.set_variable(var[0], var[1], 'int', ord(char))

        return

    def read(self, ctx: Context):
        var = self.args[0].value.split('@')
        if self.args[1].value == 'int':
            try:
                data = int(ctx.input.readline())
                ctx.set_variable(var[0], var[1], 'int', data)
            except ValueError:
                ctx.set_variable(var[0], var[1], 'nil', 'nil')
        elif self.args[1].value == 'bool':
            data = ctx.input.readline().lower()
            if data == 'true' or data == 'true\n':
                ctx.set_variable(var[0], var[1], 'bool', 'true')
            else:
                ctx.set_variable(var[0], var[1], 'bool', 'false')
        elif self.args[1].value == 'string':
            data = ctx.input.readline()
            ctx.set_variable(var[0], var[1], 'string', data)
        else:
            ctx.error('READ only accepts integer, boolean and string types.')
            exit(ExitCode.BAD_OPERAND_VALUE.value)

        return

    def write(self, ctx: Context):
        sym = ctx.get_variable_from_arg(self.args[0])
        if sym.type == 'nil':
            print('')
        elif sym.type == 'bool':
            print(sym.value)
        else:
            print(sym.value, end='')

        return

    def concat(self, ctx: Context):
        sym1 = ctx.get_variable_from_arg(self.args[1])
        sym2 = ctx.get_variable_from_arg(self.args[2])
        if sym1.type != 'string' or sym2.type != 'string':
            ctx.error('CONCAT accepts only string parameters.')
            exit(ExitCode.BAD_OPERAND_TYPE.value)

        result = sym1.value + sym2.value

        var = self.args[0].value.split('@')
        ctx.set_variable(var[0], var[1], 'string', result)

        return

    def strlen(self, ctx: Context):
        sym1 = ctx.get_variable_from_arg(self.args[1])
        if sym1.type != 'string':
            ctx.error('STRLEN accepts only a string parameter.')
            exit(ExitCode.BAD_OPERAND_TYPE.value)

        result = len(sym1.value)

        var = self.args[0].value.split('@')
        ctx.set_variable(var[0], var[1], 'int', result)

        return

    def getchar(self, ctx: Context):
        sym1 = ctx.get_variable_from_arg(self.args[1])
        sym2 = ctx.get_variable_from_arg(self.args[2])
        if sym1.type != 'string' or sym2.type != 'int':
            ctx.error('GETCHAR expected signature is VAR STRING INT.')
            exit(ExitCode.BAD_OPERAND_TYPE.value)
        if int(sym2.value) < 0 or int(sym2.value) >= len(sym1.value):
            ctx.error('Index is out of range.')
            exit(ExitCode.BAD_STRING.value)

        result = sym1.value[int(sym2.value)]

        var = self.args[0].value.split('@')
        ctx.set_variable(var[0], var[1], 'string', result)
        return

    def setchar(self, ctx: Context):
        var_data = self.args[0].value.split('@')
        var = ctx.get_variable(var_data[0], var_data[1])
        sym1 = ctx.get_variable_from_arg(self.args[1])
        sym2 = ctx.get_variable_from_arg(self.args[2])
        if var.type != 'string' or sym1.type != 'int' or sym2.type != 'string':
            ctx.error('SETCHAR expected signature is VAR(STRING) INT STRING.')
            exit(ExitCode.BAD_OPERAND_TYPE.value)
        if int(sym1.value) < 0 or int(sym1.value) >= len(var.value):
            ctx.error('Index is out of range.')
            exit(ExitCode.BAD_STRING.value)
        if sym2.value == '':
            ctx.error('Char can\'t be empty.')
            exit(ExitCode.BAD_STRING.value)

        var.value = var.value[:int(sym1.value)] + sym2.value[0] + var.value[int(sym1.value) + 1:]
        ctx.set_variable(var_data[0], var_data[1], 'string', var.value)
        return

    def type(self, ctx: Context):
        sym1 = ctx.get_variable_from_arg(self.args[1])
        var_data = self.args[0].value.split('@')
        ctx.set_variable(var_data[0], var_data[1], 'string', sym1.type)
        return

    def label(self, ctx: Context):
        return

    def jump(self, ctx: Context):
        ctx.jump_to_label(self.args[0].value)
        return

    def jumpifeq(self, ctx: Context):
        sym1 = ctx.get_variable_from_arg(self.args[1])
        sym2 = ctx.get_variable_from_arg(self.args[2])

        if sym1.type == 'nil' or sym2.type == 'nil':
            var = self.args[0].value.split('@')
            if sym1.type == 'nil' and sym2.type != 'nil' or sym1.type != 'nil' and sym2.type == 'nil':
                return  # do nothing
            else:
                ctx.jump_to_label(self.args[0].value)
                return

        if sym1.type != sym2.type:
            ctx.error('JUMPIFEQ only accepts parameters with equal types.')
            exit(ExitCode.BAD_OPERAND_TYPE.value)

        if sym1.type == 'int':
            if int(sym1.value) == int(sym2.value):
                ctx.jump_to_label(self.args[0].value)
        else:
            if sym1.value == sym2.value:
                ctx.jump_to_label(self.args[0].value)
        return

    def jumpifneq(self, ctx: Context):
        sym1 = ctx.get_variable_from_arg(self.args[1])
        sym2 = ctx.get_variable_from_arg(self.args[2])

        if sym1.type == 'nil' or sym2.type == 'nil':
            var = self.args[0].value.split('@')
            if sym1.type == 'nil' and sym2.type != 'nil' or sym1.type != 'nil' and sym2.type == 'nil':
                ctx.jump_to_label(self.args[0].value)
                return
            else:
                return

        if sym1.type != sym2.type:
            ctx.error('JUMPIFNEQ only accepts parameters with equal types.')
            exit(ExitCode.BAD_OPERAND_TYPE.value)

        if sym1.type == 'int':
            if int(sym1.value) != int(sym2.value):
                ctx.jump_to_label(self.args[0].value)
        else:
            if sym1.value != sym2.value:
                ctx.jump_to_label(self.args[0].value)
        return

    def exit(self, ctx: Context):
        sym1 = ctx.get_variable_from_arg(self.args[0])
        if sym1.type != 'int':
            ctx.error('EXIT only accepts an integer parameter.')
            exit(ExitCode.BAD_OPERAND_TYPE.value)

        val = int(sym1.value)
        if val < 0 or val > 49:
            ctx.error('EXIT parameter should be in 0-49 range.')
            exit(ExitCode.BAD_OPERAND_VALUE.value)

        exit(val)

        return

    def dprint(self, ctx: Context):
        sym1 = ctx.get_variable_from_arg(self.args[0])
        print(sym1.value, file=sys.stderr)
        return

    def exec_break(self, ctx: Context):
        result = f'Current instruction: {ctx.current_pos}\n'
        result += f'Stack ({len(ctx.stack)} elements):\n'

        index = -1
        for v in ctx.stack:
            result += f'({(index + 1) / -1}) {v}\n'

        result += f'\nGF ({len(ctx.GF)} elements):\n'
        for el in ctx.GF:
            result += f'{el} = {ctx.GF[el]}\n'

        if len(ctx.LFs) != 0:
            result += f'\nLF ({len(ctx.LFs[-1])} elements):\n'
            for el in ctx.GF:
                result += f'{el} = {ctx.LFs[-1][el]}\n'
        else:
            result += 'LF does not exist.\n'

        if ctx.TF is not None:
            result += f'\nGF ({len(ctx.TF)} elements):\n'
            for el in ctx.TF:
                result += f'{el} = {ctx.TF[el]}\n'
        else:
            result += 'TF does not exist.\n'

        print(result, file=sys.stderr, end='')
        return
