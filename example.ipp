.IPPcode22
DEFVAR GF@counter
MOVE GF@counter string@ #Inicializace proměnné na prázdný řetězec
#Jednoduchá iterace , dokud nebude splněna zadaná podmínka
LABEL while
JUMPIFEQ end GF@counter string@aaa
WRITE string@Proměnná\032GF@counter\032obsahuje\032
WRITE GF@counter
WRITE string@\010
CONCAT GF@counter GF@counter string@a
JUMP while
LABEL end
