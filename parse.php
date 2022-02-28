<?php
/*
 * Project: IPPcode22 language parser
 * Brno University of Technology | Faculty of Information Technology
 * Course: Principles of Programming Languages | Summer semester 2022
 * Author: Denis Karev (xkarev00@stud.fit.vutbr.cz)
 * This project should not be used for non-educational purposes.
 */

ini_set('display_errors', 'stderr');

$header = false;
$instructionOrder = 1;
$lineIndex = 0;

/**
 * Parser error codes
 */
enum ErrorCode: int
{
    case INVALID_ARGUMENT = 10;
    case INVALID_HEADER = 21;
    case INVALID_OPCODE = 22;
    case PARSER_ERROR = 23;
    case INTERNAL_ERROR = 99;
}

/**
 * Possible variations of instruction's arguments
 */
enum InstructionArgType
{
    case NOARG;
    case VAR;
    case LABEL;
    case SYM;
    case VAR_SYM;
    case VAR_SYM_SYM;
    case VAR_TYPE;
    case LABEL_SYM_SYM;
}

/**
 * Types of instruction arguments
 */
enum ArgType: string
{
    case VAR = 'var';
    case NIL = 'nil';
    case INT = 'int';
    case BOOL = 'bool';
    case STRING = 'string';
    case LABEL = 'label';
    case SYMBOL = 'symbol';
    case TYPE = 'type';
}

function strToArgType(string $str): ArgType|null
{
    return match ($str) {
        'var' => ArgType::VAR,
        'nil' => ArgType::NIL,
        'int' => ArgType::INT,
        'bool' => ArgType::BOOL,
        'string' => ArgType::STRING,
        'label' => ArgType::LABEL,
        'symbol' => ArgType::SYMBOL,
        'type' => ArgType::TYPE,
        default => null
    };
}

/**
 * Types of symbols
 */
enum SymbolType
{
    case CONST;
    case VAR;
}

/**
 * @param string $opcode Operation code of the instruction
 * @return InstructionArgType|null Instruction's arguments type or null if the instruction doesn't exist
 */
function getInstructionArgType(string $opcode): InstructionArgType|null
{
    $instructions = array(
        'MOVE' => InstructionArgType::VAR_SYM,
        'CREATEFRAME' => InstructionArgType::NOARG,
        'PUSHFRAME' => InstructionArgType::NOARG,
        'POPFRAME' => InstructionArgType::NOARG,
        'DEFVAR' => InstructionArgType::VAR,
        'CALL' => InstructionArgType::LABEL,
        'RETURN' => InstructionArgType::NOARG,
        'PUSHS' => InstructionArgType::SYM,
        'POPS' => InstructionArgType::VAR,
        'ADD' => InstructionArgType::VAR_SYM_SYM,
        'SUB' => InstructionArgType::VAR_SYM_SYM,
        'MUL' => InstructionArgType::VAR_SYM_SYM,
        'IDIV' => InstructionArgType::VAR_SYM_SYM,
        'LT' => InstructionArgType::VAR_SYM_SYM,
        'GT' => InstructionArgType::VAR_SYM_SYM,
        'EQ' => InstructionArgType::VAR_SYM_SYM,
        'AND' => InstructionArgType::VAR_SYM_SYM,
        'OR' => InstructionArgType::VAR_SYM_SYM,
        'NOT' => InstructionArgType::VAR_SYM_SYM,
        'INT2CHAR' => InstructionArgType::VAR_SYM_SYM,
        'STR2INT' => InstructionArgType::VAR_SYM_SYM,
        'READ' => InstructionArgType::VAR_TYPE,
        'WRITE' => InstructionArgType::SYM,
        'CONCAT' => InstructionArgType::VAR_SYM_SYM,
        'STRLEN' => InstructionArgType::VAR_SYM,
        'GETCHAR' => InstructionArgType::VAR_SYM_SYM,
        'SETCHAR' => InstructionArgType::VAR_SYM_SYM,
        'TYPE' => InstructionArgType::VAR_SYM,
        'LABEL' => InstructionArgType::LABEL,
        'JUMP' => InstructionArgType::LABEL,
        'JUMPIFEQ' => InstructionArgType::LABEL_SYM_SYM,
        'EXIT' => InstructionArgType::SYM,
        'DPRINT' => InstructionArgType::SYM,
        'BREAK' => InstructionArgType::NOARG
    );

    if (!key_exists($opcode, $instructions)) return null;
    else return $instructions[$opcode];
}

/**
 * @param InstructionArgType $instructionArgType Instruction's argument type
 * @return array Array of ArgType in the correct order
 */
function getArgTypes(InstructionArgType $instructionArgType): array
{
    return match ($instructionArgType) {
        InstructionArgType::VAR => array(ArgType::VAR),
        InstructionArgType::LABEL => array(ArgType::LABEL),
        InstructionArgType::SYM => array(ArgType::SYMBOL),
        InstructionArgType::VAR_SYM => array(ArgType::VAR, ArgType::SYMBOL),
        InstructionArgType::VAR_TYPE => array(ArgType::VAR, ArgType::TYPE),
        InstructionArgType::VAR_SYM_SYM => array(ArgType::VAR, ArgType::SYMBOL, ArgType::SYMBOL),
        InstructionArgType::LABEL_SYM_SYM => array(ArgType::LABEL, ArgType::SYMBOL, ArgType::SYMBOL),
        default => array(),
    };
}

/**
 * Gets symbol type
 * @param string $symbol Symbol
 * @return SymbolType|null Type of the symbol (var/const) or null if value is not a symbol
 */
function getSymbolType(string $symbol): SymbolType|null
{
    $separatorPos = strpos($symbol, '@');
    if ($separatorPos == null) return null;

    $left = substr($symbol, 0, $separatorPos);
    if ($left == 'GF' || $left == 'TF' || $left == 'LF')
        return SymbolType::VAR;
    else
        return SymbolType::CONST;
}

/**
 * Prints the help message
 */
function printHelp()
{
    echo "IPPcode22 parser\n\n";
    echo "Allowed arguments:\n";
    echo "\t--help - prints this message\n";
}

/**
 * Prints error message and exits with the specified error code
 * @param ErrorCode $code Error code
 * @param string $message Error message
 * @return void
 */
function error(ErrorCode $code, string $message)
{
    fwrite(STDERR, $message);
    exit($code->value);
}

/**
 * Parses the command line arguments
 * @param int $argc Argument count
 * @param array $argv Command line arguments
 * @return void
 */
function parseCLIArgs(int $argc, array $argv)
{
    if ($argc >= 2) {
        if ($argc == 2 && $argv[1] == '--help') {
            printHelp();
            exit(0);
        } else {
            error(ErrorCode::INVALID_ARGUMENT, "The only allowed argument is --help.");
        }
    }
}

/**
 * Removes all comments from the line
 * @param string $line Input line
 * @return string Input line without comments
 */
function trimComment(string $line)
{
    $comment_pos = strpos($line, '#');
    if (!$comment_pos) return $line;

    return substr($line, 0, $comment_pos);
}

/**
 * Checks if variable name is correct (contains only allowed symbols)
 * @param string $value Variable or label name
 */
function validateVariableName(string $value): void
{
    global $lineIndex;
    if (!preg_match("/^[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$/", $value))
        error(ErrorCode::PARSER_ERROR, "Line $lineIndex: '$value' is an incorrect name for a label or variable");
}

/**
 * Checks if the specified type name is valid (int, string, bool or nil)
 * @param string $value Type name to check
 */
function validateTypeName(string $value): void
{
    global $lineIndex;
    if ($value != 'int' && $value != 'string' && $value != 'bool' && $value != 'nil')
        error(ErrorCode::PARSER_ERROR, "Line $lineIndex: expected type, but got '$value'");
}

/**
 * Validates a variable
 * @param string $var Variable to validate
 */
function validateVariable(string $var): void
{
    global $lineIndex;

    $separatorPos = strpos($var, '@');
    if ($separatorPos == null)
        error(ErrorCode::PARSER_ERROR, "Line $lineIndex: expected '$var' to be a variable");
    if ($separatorPos == 0)
        error(ErrorCode::PARSER_ERROR, "Line $lineIndex: missing frame name in '$var'");
    if ($separatorPos == strlen($var) - 1)
        error(ErrorCode::PARSER_ERROR, "Line $lineIndex: missing variable name in '$var'");

    $frame = substr($var, 0, $separatorPos);
    validateFrameName($frame);
    $varName = substr($var, $separatorPos + 1, strlen($var));
    validateVariableName($varName);
}

/**
 * Checks if the specified frame name is correct (GF, TF or LF)
 * @param string $value Frame name to check
 */
function validateFrameName(string $value): void
{
    global $lineIndex;

    if ($value != 'GF' && $value != 'TF' && $value != 'LF')
        error(ErrorCode::PARSER_ERROR, "Line $lineIndex: expected frame, but got '$value'");
}

/**
 * Validates symbol and determines its type and value
 * @param string $value Symbol to validate
 * @return array Array with type and val fields.
 */
function validateSymbol(string $value): array
{
    global $lineIndex;

    $symbolType = getSymbolType($value);
    if ($symbolType == null)
        error(ErrorCode::PARSER_ERROR, "Line $lineIndex: expected symbol, but got '$value'");

    $separatorPos = strpos($value, '@');
    if ($symbolType == SymbolType::CONST) {
        $type = substr($value, 0, $separatorPos);
        validateTypeName($type);
        $constValue = substr($value, $separatorPos + 1, strlen($value));
        validateConstantValue($constValue, strToArgType($type));
        return array('type' => strToArgType($type), 'val' => $constValue);
    } else {
        validateVariable($value);
        return array('type' => ArgType::VAR, 'val' => $value);
    }
}

/**
 * Checks if the specified constant value matches the specified type
 * @param string $value Constant value
 * @param ArgType $expectedType Constant type
 */
function validateConstantValue(string $value, ArgType $expectedType)
{
    global $lineIndex;

    switch ($expectedType) {
        case ArgType::NIL:
            if ($value != 'nil')
                error(ErrorCode::PARSER_ERROR, "Line $lineIndex: expected '$value' to be nil.");
            break;
        case ArgType::BOOL:
            if ($value != 'true' && $value != 'false')
                error(ErrorCode::PARSER_ERROR, "Line $lineIndex: expected '$value' to be bool.");
            break;
        case ArgType::INT:
            if (!preg_match("/^[+-]?[\d]+$/", $value))
                error(ErrorCode::PARSER_ERROR, "Line $lineIndex: expected '$value' to be int.");
            break;
        case ArgType::STRING:
            // Error isn't possible here as string can contain any chars except for special ones, but they are controlled in other places
            break;
        default:
            error(ErrorCode::INTERNAL_ERROR, "Line $lineIndex: unexpected type while validating constant.");
    }
}

/**
 * Parses argument, checks if it is correct and returns its type and value
 * @param string $arg Argument to parse
 * @param ArgType $argType Expected argument type
 * @return array Array, containing type and val fields
 */
function parseArgument(string $arg, ArgType $argType): array
{
    $retType = $argType;
    $retVal = $arg;
    if ($argType == ArgType::LABEL)
        validateVariableName($arg);
    else if ($argType == ArgType::TYPE)
        validateTypeName($arg);
    else if ($argType == ArgType::VAR)
        validateVariable($arg);
    else if ($argType == ArgType::SYMBOL) {
        $symbolData = validateSymbol($arg);

        $retType = $symbolData['type'];
        $retVal = $symbolData['val'];
    }

    return array('type' => $retType, 'val' => $retVal);
}

/**
 * Writes argument information to XML
 * @param int $argIndex Argument index (1-3)
 * @param ArgType $argType Argument type
 * @param mixed $argVal Argument value
 */
function writeArgInfo(int $argIndex, ArgType $argType, mixed $argVal)
{
    global $xw;
    $xw->startElement("arg$argIndex");
    $xw->writeAttribute('type', $argType->value);
    $xw->text($argVal);
    $xw->endElement();
}

/**
 * Validates opcode, argument count, initiates argument validations and writes information to XML
 * @param array $instruction Instruction without comments and separated by white-chars
 */
function validateInstruction(array $instruction)
{
    global $instructionOrder, $lineIndex, $xw;

    $argType = getInstructionArgType($instruction[0]);
    if ($argType == null)
        error(ErrorCode::INVALID_OPCODE, "Line $lineIndex: unknown opcode $instruction[0].");

    $argTypes = getArgTypes($argType);
    $expectedArgCount = sizeof($argTypes);
    $actualArgCount = sizeof($instruction) - 1;

    if ($actualArgCount != $expectedArgCount)
        error(ErrorCode::PARSER_ERROR, "Line $lineIndex: expected $expectedArgCount arguments for opcode $instruction[0], but got $actualArgCount");

    $xw->startElement('instruction');

    $xw->writeAttribute('order', $instructionOrder);
    $instructionOrder++;
    $xw->writeAttribute('opcode', $instruction[0]);

    for ($i = 1; $i <= $expectedArgCount; ++$i) {
        $argInfo = parseArgument($instruction[$i], $argTypes[$i - 1]);
        writeArgInfo($i, $argInfo['type'], $argInfo['val']);
    }

    $xw->endElement();
}

/**
 * Reads input from stdin and parses it.
 */
function parseInput()
{
    global $header, $lineIndex, $xw;

    while ($line = fgets(STDIN)) {
        $lineIndex += 1;
        if ($line == '\n' || $line[0] == '#') continue;

        $trimmed = trim(trimComment($line));
        $instruction = preg_split('/\s+/', $trimmed);

        $instruction[0] = strtoupper($instruction[0]); // as opcode is case-insensitive

        if (!$header) {
            if ($instruction[0] == '.IPPCODE22') $header = true;
            else error(ErrorCode::INVALID_HEADER, "Line $lineIndex: expected header .IPPcode22, but got: $line.");

            $xw->startElement('program');
            $xw->writeAttribute('language', 'IPPcode22');
            continue;
        }

        validateInstruction($instruction);
    }
}


$xw = new XMLWriter();
$xw->openMemory();
$xw->setIndent(true);
$xw->startDocument('1.0', 'UTF-8');

parseCLIArgs($argc, $argv);
parseInput($xw);
if (!$header)
    error(ErrorCode::INVALID_HEADER, "Input was empty");

$xw->endElement();
$xw->endDocument();
echo $xw->outputMemory();
