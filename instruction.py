import sys

from argument import Argument
from context import Context
from exit_code import ExitCode
from logic import LogicType, LogicEvaluator
from type_checker import TypeChecker
from variable import Variable
from arithmetics import ArithmeticEvaluator, ArithmeticsType


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
        elif self.opcode == "CLEARS":
            self.clears(ctx)
        elif self.opcode == "ADDS":
            self.adds(ctx)
        elif self.opcode == "SUBS":
            self.subs(ctx)
        elif self.opcode == "MULS":
            self.muls(ctx)
        elif self.opcode == "IDIVS":
            self.idivs(ctx)
        elif self.opcode == "LTS":
            self.lts(ctx)
        elif self.opcode == "GTS":
            self.gts(ctx)
        elif self.opcode == "EQS":
            self.eqs(ctx)
        elif self.opcode == "ANDS":
            self.ands(ctx)
        elif self.opcode == "ORS":
            self.ors(ctx)
        elif self.opcode == "NOTS":
            self.nots(ctx)
        elif self.opcode == "INT2CHARS":
            self.int2chars(ctx)
        elif self.opcode == "STRI2INTS":
            self.stri2ints(ctx)
        elif self.opcode == "JUMPIFEQS":
            self.jumpifeqs(ctx)
        elif self.opcode == "JUMPIFNEQS":
            self.jumpifneqs(ctx)
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
        elif self.opcode == "DIV":
            self.div(ctx)
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
        else:
            ctx.error(f'unknown opcode {self.opcode}.')
            exit(ExitCode.UNEXPECTED_XML_STRUCTURE.value)

        self.update_stats(ctx)

    def update_stats(self, ctx: Context):
        if (self.opcode, self.order) not in ctx.stats.hot.keys():
            ctx.stats.hot[(self.opcode, self.order)] = 0
        ctx.stats.hot[(self.opcode, self.order)] += 1

        if self.opcode != 'DPRINT' and self.opcode != 'LABEL' and self.opcode != 'BREAK':
            ctx.stats.insts += 1

    # Gets a variable from its identifier in the argument and stores there the specified value
    def update_var_in_args(self, ctx: Context, type: str, value, arg_index: int = 0):
        var_data = self.args[0].value.split('@')
        ctx.set_variable(var_data[0], var_data[1], type, value)

    # region Frames and variables
    def move(self, ctx: Context):
        sym = ctx.get_variable_from_arg(self.args[1])
        self.update_var_in_args(ctx, sym.type, sym.value)
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
            exit(ExitCode.UNDEFINED_FRAME.value)

        ctx.TF = ctx.LFs.pop()
        return

    def defvar(self, ctx: Context):
        data = self.args[0].value.split('@')
        ctx.def_var(data[0], data[1])
        return

    def call(self, ctx: Context):
        ctx.calls.append(self.order - 1)
        ctx.jump_to_label(self.args[0].value)
        return

    def exec_return(self, ctx: Context):
        if len(ctx.calls) == 0:
            ctx.error('call frame is empty.')
            exit(ExitCode.MISSING_VALUE.value)

        ctx.current_pos = ctx.calls.pop()
        return
    # endregion

    # region Stack
    def check_stack_len(self, ctx: Context, required_stack_len: int):
        if len(ctx.stack) < required_stack_len:
            ctx.error(f'Stack has {len(ctx.stack)} elements but {self.opcode} requires {required_stack_len}')
            exit(ExitCode.MISSING_VALUE.value)

    def pushs(self, ctx: Context):
        var = ctx.get_variable_from_arg(self.args[0])

        ctx.stack.append(var)
        return

    def pops(self, ctx: Context):
        self.check_stack_len(ctx, 1)
        var = ctx.stack.pop()

        self.update_var_in_args(ctx, var.type, var.value)
        return

    def clears(self, ctx: Context):
        ctx.stack = []
        return

    def adds(self, ctx: Context):
        self.check_stack_len(ctx, 2)
        sym2 = ctx.stack.pop()
        sym1 = ctx.stack.pop()

        result = self.calc_arithmetics(sym1, sym2, ctx, ArithmeticsType.ADD)
        ctx.stack.append(Variable(sym1.type, result))
        return

    def subs(self, ctx: Context):
        self.check_stack_len(ctx, 2)
        sym2 = ctx.stack.pop()
        sym1 = ctx.stack.pop()

        result = self.calc_arithmetics(sym1, sym2, ctx, ArithmeticsType.SUB)
        ctx.stack.append(Variable(sym1.type, result))
        return

    def muls(self, ctx: Context):
        self.check_stack_len(ctx, 2)
        sym2 = ctx.stack.pop()
        sym1 = ctx.stack.pop()

        result = self.calc_arithmetics(sym1, sym2, ctx, ArithmeticsType.MUL)
        ctx.stack.append(Variable(sym1.type, result))
        return

    def idivs(self, ctx: Context):
        self.check_stack_len(ctx, 2)
        sym2 = ctx.stack.pop()
        sym1 = ctx.stack.pop()
        if sym2.float_value() == 0:
            ctx.error("you can't divide by zero =(")
            exit(ExitCode.BAD_OPERAND_VALUE.value)

        result = self.calc_arithmetics(sym1, sym2, ctx, ArithmeticsType.IDIV)
        ctx.stack.append(Variable(sym1.type, result))
        return

    def lts(self, ctx: Context):
        self.check_stack_len(ctx, 2)
        sym2 = ctx.stack.pop()
        sym1 = ctx.stack.pop()

        result = self.calc_logic(sym1, sym2, ctx, LogicType.LT, ['int', 'float', 'string', 'bool'])
        ctx.stack.append(Variable('bool', result))
        return

    def gts(self, ctx: Context):
        self.check_stack_len(ctx, 2)
        sym2 = ctx.stack.pop()
        sym1 = ctx.stack.pop()

        result = self.calc_logic(sym1, sym2, ctx, LogicType.GT, ['int', 'float', 'string', 'bool'])
        ctx.stack.append(Variable('bool', result))
        return

    def eqs(self, ctx: Context):
        self.check_stack_len(ctx, 2)
        sym2 = ctx.stack.pop()
        sym1 = ctx.stack.pop()

        result = self.calc_logic(sym1, sym2, ctx, LogicType.EQ, ['int', 'float', 'string', 'bool', 'nil'])
        ctx.stack.append(Variable('bool', result))
        return

    def ands(self, ctx: Context):
        self.check_stack_len(ctx, 2)
        sym2 = ctx.stack.pop()
        sym1 = ctx.stack.pop()

        result = self.calc_logic(sym1, sym2, ctx, LogicType.AND, ['bool'])
        ctx.stack.append(Variable('bool', result))
        return

    def ors(self, ctx: Context):
        self.check_stack_len(ctx, 2)
        sym2 = ctx.stack.pop()
        sym1 = ctx.stack.pop()

        result = self.calc_logic(sym1, sym2, ctx, LogicType.OR, ['bool'])
        ctx.stack.append(Variable('bool', result))
        return

    def nots(self, ctx: Context):
        self.check_stack_len(ctx, 1)
        sym1 = ctx.stack.pop()

        result = self.calc_logic(sym1, None, ctx, LogicType.NOT, ['bool'])
        ctx.stack.append(Variable('bool', result))
        return

    def int2chars(self, ctx: Context):
        self.check_stack_len(ctx, 1)
        sym1 = ctx.stack.pop()
        TypeChecker.full_check(ctx, self.opcode, sym1, ['int'])

        try:
            result = chr(int(sym1.value))
            ctx.stack.append(Variable('string', result))
        except ValueError:
            ctx.error(f'{sym1.value} is an incorrect Unicode code.')
            exit(ExitCode.BAD_STRING_OPERATION.value)
        return

    def stri2ints(self, ctx: Context):
        self.check_stack_len(ctx, 2)
        sym2 = ctx.stack.pop()
        sym1 = ctx.stack.pop()

        TypeChecker.full_check(ctx, self.opcode, sym1, ['string'])
        TypeChecker.full_check(ctx, self.opcode, sym2, ['int'])

        if int(sym2.value) < 0 or int(sym2.value) >= len(sym1.value):
            ctx.error('index is out of range.')
            exit(ExitCode.BAD_STRING_OPERATION.value)

        char = sym1.value[int(sym2.value)]
        ctx.stack.append(Variable('int', ord(char)))
        return

    def jumpifeqs(self, ctx: Context):
        self.check_stack_len(ctx, 3)
        sym2 = ctx.stack.pop()
        sym1 = ctx.stack.pop()
        label = self.args[0].value()

        result = self.calc_logic(sym1, sym2, ctx, LogicType.EQ, ['int', 'float', 'string', 'bool', 'nil'])
        if result:
            ctx.jump_to_label(label)
        return

    def jumpifneqs(self, ctx: Context):
        self.check_stack_len(ctx, 3)
        sym2 = ctx.stack.pop()
        sym1 = ctx.stack.pop()
        label = self.args[0].value()

        result = self.calc_logic(sym1, sym2, ctx, LogicType.EQ, ['int', 'float', 'string', 'bool', 'nil'])
        if not result:
            ctx.jump_to_label(label)
        return

    # endregion

    # region Maths
    def calc_arithmetics(self, var1: Variable, var2: Variable, ctx: Context, op_type: ArithmeticsType, allowed_types=None) -> int or float:
        if allowed_types is None:
            allowed_types = ['int', 'float']

        TypeChecker.full_check(ctx, self.opcode, var1, allowed_types)
        TypeChecker.full_check(ctx, self.opcode, var2, allowed_types)

        if var1.type != var2.type:
            ctx.error(f"operands must have the same type. Current types: {var1.type} and {var2.type}")
            exit(ExitCode.BAD_OPERAND_TYPE.value)

        value1 = None
        value2 = None

        if var1.type == 'int':
            value1 = int(var1.value)
            value2 = int(var2.value)
        elif var2.type == 'float':
            value1 = var1.float_value()
            value2 = var2.float_value()

        return ArithmeticEvaluator(value1, value2, op_type).eval()

    def int2float(self, ctx: Context):
        sym1 = ctx.get_variable_from_arg(self.args[1])
        if sym1.type != 'int':
            ctx.error('INT2FLOAT accepts only integer parameters.')
            exit(ExitCode.BAD_OPERAND_TYPE.value)

        val = float(sym1.value)
        var = self.args[0].value.split('@')
        ctx.set_variable(var[0], var[1], 'float', val)

        return

    def float2int(self, ctx: Context):
        sym1 = ctx.get_variable_from_arg(self.args[1])
        if sym1.type != 'float':
            ctx.error('FLOAT2INT accepts only float parameters.')
            exit(ExitCode.BAD_OPERAND_TYPE.value)

        val = int(sym1.float_value())

        var = self.args[0].value.split('@')
        ctx.set_variable(var[0], var[1], 'int', val)

        return

    def add(self, ctx: Context):
        sym1 = ctx.get_variable_from_arg(self.args[1])
        sym2 = ctx.get_variable_from_arg(self.args[2])

        result = self.calc_arithmetics(sym1, sym2, ctx, ArithmeticsType.ADD)

        var = self.args[0].value.split('@')
        ctx.set_variable(var[0], var[1], sym1.type, result)
        return

    def sub(self, ctx: Context):
        sym1 = ctx.get_variable_from_arg(self.args[1])
        sym2 = ctx.get_variable_from_arg(self.args[2])

        result = self.calc_arithmetics(sym1, sym2, ctx, ArithmeticsType.SUB)

        var = self.args[0].value.split('@')
        ctx.set_variable(var[0], var[1], sym1.type, result)
        return

    def mul(self, ctx: Context):
        sym1 = ctx.get_variable_from_arg(self.args[1])
        sym2 = ctx.get_variable_from_arg(self.args[2])

        result = self.calc_arithmetics(sym1, sym2, ctx, ArithmeticsType.MUL)

        var = self.args[0].value.split('@')
        ctx.set_variable(var[0], var[1], sym1.type, result)
        return

    def idiv(self, ctx: Context):
        sym1 = ctx.get_variable_from_arg(self.args[1])
        sym2 = ctx.get_variable_from_arg(self.args[2])
        if sym2.float_value() == 0:
            ctx.error("you can't divide by zero =(")
            exit(ExitCode.BAD_OPERAND_VALUE.value)

        result = self.calc_arithmetics(sym1, sym2, ctx, ArithmeticsType.IDIV)

        var = self.args[0].value.split('@')
        ctx.set_variable(var[0], var[1], sym1.type, result)
        return

    def div(self, ctx):
        sym1 = ctx.get_variable_from_arg(self.args[1])
        sym2 = ctx.get_variable_from_arg(self.args[2])
        if sym2.float_value() == 0:
            ctx.error("you can't divide by zero =(")
            exit(ExitCode.BAD_OPERAND_VALUE.value)

        result = self.calc_arithmetics(sym1, sym2, ctx, ArithmeticsType.DIV, allowed_types=['float'])

        var = self.args[0].value.split('@')
        ctx.set_variable(var[0], var[1], sym1.type, result)
        return

    def calc_logic(self, var1: Variable, var2: Variable or None, ctx: Context, op_type: LogicType, allowed_types) -> bool:
        TypeChecker.full_check(ctx, self.opcode, var1, allowed_types)

        value1 = var1.unwrap()
        value2 = None

        if var2 is not None:
            TypeChecker.full_check(ctx, self.opcode, var2, allowed_types)
            if var2.type != 'nil':
                TypeChecker.var_type_check(ctx, self.opcode, var1, [var2.type, 'nil'])  # args must be of the same type or nil
            else:
                TypeChecker.var_type_check(ctx, self.opcode, var2, [var1.type, 'nil'])
            value2 = var2.unwrap()

        return LogicEvaluator(op_type, value1, value2).eval()

    def lt(self, ctx: Context):
        sym1 = ctx.get_variable_from_arg(self.args[1])
        sym2 = ctx.get_variable_from_arg(self.args[2])

        result = self.calc_logic(sym1, sym2, ctx, LogicType.LT, ['int', 'float', 'string', 'bool'])
        self.update_var_in_args(ctx, 'bool', result)
        return

    def gt(self, ctx: Context):
        sym1 = ctx.get_variable_from_arg(self.args[1])
        sym2 = ctx.get_variable_from_arg(self.args[2])

        result = self.calc_logic(sym1, sym2, ctx, LogicType.GT, ['int', 'float', 'string', 'bool'])
        self.update_var_in_args(ctx, 'bool', result)
        return

    def eq(self, ctx: Context):
        sym1 = ctx.get_variable_from_arg(self.args[1])
        sym2 = ctx.get_variable_from_arg(self.args[2])

        result = self.calc_logic(sym1, sym2, ctx, LogicType.EQ, ['int', 'float', 'string', 'bool', 'nil'])
        self.update_var_in_args(ctx, 'bool', result)
        return

    def exec_and(self, ctx: Context):
        sym1 = ctx.get_variable_from_arg(self.args[1])
        sym2 = ctx.get_variable_from_arg(self.args[2])

        result = self.calc_logic(sym1, sym2, ctx, LogicType.AND, ['bool'])
        self.update_var_in_args(ctx, 'bool', result)
        return

    def exec_or(self, ctx: Context):
        sym1 = ctx.get_variable_from_arg(self.args[1])
        sym2 = ctx.get_variable_from_arg(self.args[2])

        result = self.calc_logic(sym1, sym2, ctx, LogicType.OR, ['bool'])
        self.update_var_in_args(ctx, 'bool', result)
        return

    def exec_not(self, ctx: Context):
        sym1 = ctx.get_variable_from_arg(self.args[1])

        result = self.calc_logic(sym1, None, ctx, LogicType.NOT, ['bool'])
        self.update_var_in_args(ctx, 'bool', result)
        return

    def int2char(self, ctx: Context):
        sym1 = ctx.get_variable_from_arg(self.args[1])
        TypeChecker.full_check(ctx, self.opcode, sym1, ['int'])

        try:
            result = chr(int(sym1.value))
            var = self.args[0].value.split('@')
            ctx.set_variable(var[0], var[1], 'string', result)
        except ValueError:
            ctx.error(f'{sym1.value} is an incorrect Unicode code.')
            exit(ExitCode.BAD_STRING_OPERATION.value)
        return

    def stri2int(self, ctx: Context):
        sym1 = ctx.get_variable_from_arg(self.args[1])
        sym2 = ctx.get_variable_from_arg(self.args[2])

        TypeChecker.full_check(ctx, self.opcode, sym1, ['string'])
        TypeChecker.full_check(ctx, self.opcode, sym2, ['int'])

        if int(sym2.value) < 0 or int(sym2.value) >= len(sym1.value):
            ctx.error('index is out of range.')
            exit(ExitCode.BAD_STRING_OPERATION.value)

        char = sym1.value[int(sym2.value)]
        var = self.args[0].value.split('@')
        ctx.set_variable(var[0], var[1], 'int', ord(char))
        return
    # endregion

    # region I/O
    def read(self, ctx: Context):
        var = self.args[0].value.split('@')
        if self.args[1].value == 'int':
            try:
                data = int(ctx.input.readline())
                ctx.set_variable(var[0], var[1], 'int', data)
            except ValueError:
                ctx.set_variable(var[0], var[1], 'nil', 'nil')
        elif self.args[1].value == 'float':
            f_input = ctx.input.readline()
            try:
                data = float(f_input)
                ctx.set_variable(var[0], var[1], 'float', data)
            except ValueError:
                try:
                    data = float.fromhex(f_input)
                    ctx.set_variable(var[0], var[1], 'float', data)
                except ValueError:
                    ctx.set_variable(var[0], var[1], 'nil', 'nil')
        elif self.args[1].value == 'bool':
            data = ctx.input.readline().lower()
            if data == 'true' or data == 'true\n':
                ctx.set_variable(var[0], var[1], 'bool', 'true')
            else:
                ctx.set_variable(var[0], var[1], 'bool', 'false')
        elif self.args[1].value == 'string':
            data = ctx.input.readline().rstrip('\n')
            ctx.set_variable(var[0], var[1], 'string', data)
        else:
            ctx.error('READ only accepts integer, float, boolean and string types.')
            exit(ExitCode.BAD_OPERAND_VALUE.value)

        return

    def write(self, ctx: Context):
        sym = ctx.get_variable_from_arg(self.args[0])
        TypeChecker.full_check(ctx, self.opcode, sym, ['int', 'float', 'bool', 'nil', 'string'])

        output = sym.value
        if sym.type == 'nil':
            output = ''
        elif sym.type == 'string':
            for i in range(999):
                number = "\\{:03d}".format(i)
                sym.value = sym.value.replace(number, chr(i))
            output = sym.value
        elif sym.type == 'float':
            output = sym.float_value().hex()

        print(output, end='')

        return
    # endregion

    # region Strings
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
            exit(ExitCode.BAD_STRING_OPERATION.value)

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
            exit(ExitCode.BAD_STRING_OPERATION.value)
        if sym2.value == '':
            ctx.error('Char can\'t be empty.')
            exit(ExitCode.BAD_STRING_OPERATION.value)

        var.value = var.value[:int(sym1.value)] + sym2.value[0] + var.value[int(sym1.value) + 1:]
        ctx.set_variable(var_data[0], var_data[1], 'string', var.value)
        return
    # endregion

    # region Types
    def type(self, ctx: Context):
        sym1 = ctx.get_variable_from_arg(self.args[1])
        var_data = self.args[0].value.split('@')
        ctx.set_variable(var_data[0], var_data[1], 'string', sym1.type)
        return
    # endregion

    # region Flow
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
        elif sym1.type == 'float':
            if sym1.float_value() == sym2.float_value():
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
        elif sym1.type == 'float':
            if sym1.float_value() != sym2.float_value():
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
    # endregion

    # region Debug
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
    # endregion
