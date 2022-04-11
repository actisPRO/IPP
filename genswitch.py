input = """MOVE
CREATEFRAME
PUSHFRAME
POPFRAME
DEFVAR
CALL
RETURN
PUSHS
POPS
ADD
SUB
MUL
IDIV
LT
GT
EQ
AND
OR
NOT
INT2CHAR
STRI2INT
READ
WRITE
CONCAT
STRLEN
GETCHAR
SETCHAR
TYPE
LABEL
JUMP
JUMPIFEQ
JUMPIFNEQ
EXIT
DPRINT
BREAK"""

input = input.split('\n')

result = ''
for c in input:
    result += f'        elif self.opcode == "{c}":\n' \
              f'            self.{c.lower()}(ctx)\n'


print(result)
