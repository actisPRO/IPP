from context import Context
from exit_code import ExitCode
from variable import Variable


class TypeChecker:
    @staticmethod
    def str_is_int(const_val: str) -> bool:
        try:
            int(const_val)
            return True
        except ValueError:
            return False

    @staticmethod
    def str_is_float(const_val: str) -> bool:
        try:
            float(const_val)
            return True
        except ValueError:
            return False

    @staticmethod
    def full_type_check(ctx: Context, caller_name: str, variable: Variable, accepted_types: list):
        TypeChecker.str_convertable_check(ctx, variable)
        TypeChecker.var_type_check(accepted_types, caller_name, ctx, variable)

    @staticmethod
    def var_type_check(accepted_types, caller_name, ctx, variable):
        type_check = False
        for t in accepted_types:
            if variable.type == t:
                type_check = True

        if not type_check:
            ctx.error(
                f"{caller_name} accepts only {', '.join(accepted_types)} arguments, but {variable.value} is of type {variable.type}")
            exit(ExitCode.BAD_OPERAND_TYPE.value)

    @staticmethod
    def str_convertable_check(ctx, variable):
        convertible_check_functions = {
            'int': TypeChecker.str_is_int,
            'float': TypeChecker.str_is_float
        }
        if variable.type in convertible_check_functions.keys():
            is_convertable = convertible_check_functions[variable.type](variable.value)
        else:
            is_convertable = True

        if not is_convertable:
            ctx.error(f"Value {variable.value} can't be converted to {variable.type}. Check your XML source.")
            exit(ExitCode.UNEXPECTED_XML_STRUCTURE.value)
