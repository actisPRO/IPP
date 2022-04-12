<?php
$directory = getcwd();
$recursive = false;
$parseScript = 'parse.php';
$intScript = 'interpret.py';
$parseOnly = false;
$intOnly = false;
$jExamXmlPath = '/pub/courses/ipp/jexamxml';
$noclean = false;

enum ExitCode: int
{
    case BAD_ARGUMENT = 10;
    case BAD_PATH = 41;
}

function error(ExitCode $exitCode, string $message)
{
    fwrite(STDERR, "ERROR: " . $message);
    exit($exitCode->value);
}

function printHelp()
{
    echo "IPPcode22 parser and interpreter tester\n\n"
        . "Arguments:\n"
        . "\t--help\t\t\t\t\tPrint this message and exit\n"
        . "\t--directory=path\t\tSets the test directory\n"
        . "\t--recursive\t\t\t\tIf set, tests will be searched recursively.\n"
        . "\t--parse-script=file\t\tPath to the parser script\n"
        . "\t--int-script=file\t\tPath to the interpreter script\n"
        . "\t--parse-only\t\t\tIf set, only the parser script will be tested\n"
        . "\t--jexampath=path\t\tPath to the folder containing the jexamxml.jar file\n"
        . "\t--noclean\t\t\t\tIf set, temporary files won't be removed";
}

function splitArg(string $arg): array
{
    $res = preg_split('/=/', $arg);
    if ($res == false || $res[1] == null)
        error(ExitCode::BAD_ARGUMENT, "$arg doesn't have a value.");

    return $res;
}

function parseArgs()
{
    global $argc, $argv;
    global $directory, $recursive, $parseScript, $intScript, $parseOnly, $intOnly, $jExamXmlPath, $noclean;

    $intOnlySet = false;
    $parseOnlySet = false;
    $parseScriptSet = false;
    $intScriptSet = false;

    for ($i = 1; $i < $argc; ++$i) {
        if ($argv[$i] == '--help') {
            printHelp();
            exit(0);
        } else if (str_starts_with($argv[$i], '--directory=')) {
            $arg = splitArg($argv[$i]);
            $directory = $arg[1];
        } else if ($argv[$i] == '--recursive') {
            $recursive = true;
        } else if (str_starts_with($argv[$i], '--parse-script=')) {
            $arg = splitArg($argv[$i]);
            $parseScript = $arg[1];
            $parseScriptSet = true;
        } else if (str_starts_with($argv[$i], '--int-script=')) {
            $arg = splitArg($argv[$i]);
            $intScript = $arg[1];
            $intScriptSet = true;
        } else if ($argv[$i] == '--parse-only') {
            $parseOnly = true;
            $parseOnlySet = true;
        } else if ($argv[$i] == '--int-only') {
            $intOnly = true;
            $intOnlySet = true;
        } else if (str_starts_with($argv[$i], '--jexampath=')) {
            $arg = splitArg($argv[$i]);
            $jExamXmlPath = $arg[1];
        } else if ($argv[$i] == '--noclean') {
            $noclean = true;
        }
    }

    if ($parseOnlySet && ($intOnlySet || $intScriptSet)) {
        error(ExitCode::BAD_ARGUMENT, "Can't combine --parse-only with --int-only or --int-script");
    }
    if ($intOnlySet && ($parseOnlySet || $parseScriptSet)) {
        error(ExitCode::BAD_ARGUMENT, "Can't combine --int-only with --parse-only or --parse-script");
    }
}

function findTestsInFolder(string $directory): array {
    global $recursive;

    if (!is_dir($directory))
        error(ExitCode::BAD_PATH, "Path $directory does not exist.");

    $content = scandir($directory);

    $result = [];
    foreach ($content as $item) {
        if ($item == '.' or $item == '..') continue;
        else if (is_dir($item) && $recursive) {
            $tests = findTestsInFolder($directory . '/' . $item);
            foreach ($tests as $test)
                $result[] = $test;
        } else {
            if (str_ends_with($item, '.src')) {
                $name = substr($item, 0, -4);
                $result[] = $name;
            }
        }
    }

    return $result;
}

parseArgs();
$tests = findTestsInFolder($directory);