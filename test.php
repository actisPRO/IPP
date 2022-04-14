<?php
// Global config
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
    case INTERNAL_ERROR = 99;
}

/**
 * Prints the specified error messages and exits with the specified ExitCode
 * @param ExitCode $exitCode
 * @param string $message
 */
function error(ExitCode $exitCode, string $message)
{
    fwrite(STDERR, "ERROR: " . $message . "\n");
    exit($exitCode->value);
}

/**
 * Prints the help message
 */
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

/**
 * Splits the command-line argument by the "=" sign.
 * @param string $arg Argument to split
 * @return array Splitted argument
 */
function splitArg(string $arg): array
{
    $res = preg_split('/=/', $arg);
    if ($res == false || $res[1] == null)
        error(ExitCode::BAD_ARGUMENT, "$arg doesn't have a value.");

    return $res;
}

/**
 * Reads command-line arguments, performs necessary checks and sets global properties.
 */
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

    if (!file_exists($parseScript) && !$intOnly)
        error(ExitCode::BAD_PATH, "File $parseScript does not exist.");
    if (!file_exists($intScript) && !$parseOnly)
        error(ExitCode::BAD_PATH, "File $intScript does not exist.");
}

/**
 * Creates missing test files if necessary
 * @param string $path Path to the test folder
 * @param string $testName Test name which will be used for the newly created files
 */
function checkAndCreateTestFiles(string $path, string $testName)
{
    if (!file_exists("$path/$testName.in")) {
        $file = fopen("$path/$testName.in", 'w');
        fclose($file);
    }

    if (!file_exists("$path/$testName.out")) {
        $file = fopen("$path/$testName.out", 'w');
        fclose($file);
    }

    if (!file_exists("$path/$testName.rc")) {
        $file = fopen("$path/$testName.rc", 'w');
        fwrite($file, '0');
        fclose($file);
    }
}

/**
 * Looks for *.src files in the specified folder
 * @param string $directory Folder to search in
 * @return array Test paths in format dir/testname without .src
 */
function findTestsInFolder(string $directory): array
{
    global $recursive;

    if (!is_dir($directory))
        error(ExitCode::BAD_PATH, "Path $directory does not exist.");

    $content = scandir($directory);

    $result = [];
    foreach ($content as $item) {
        if ($item == '.' or $item == '..') continue;
        else if (is_dir($directory . '/' . $item) && $recursive) {
            $tests = findTestsInFolder($directory . '/' . $item);
            foreach ($tests as $test)
                $result[] = $test;
        } else {
            if (str_ends_with($item, '.src')) {
                $name = substr($item, 0, -4);
                checkAndCreateTestFiles($directory, $name);
                $result[] = $directory . '/' . $name;
            }
        }
    }

    return $result;
}

/**
 * Executes the parser on the specified test
 * @param string $test Path to the test without extension
 * @return array out - output text (including stderr), type - xml, code - parser exit code
 */
function runParser(string $test): array
{
    global $parseScript;

    $sh = "cat $test.src | php8.1 $parseScript 2>&1";
    $output = [];

    exec($sh, $output, $exitCode);
    return array(
        'out' => implode("\n", $output),
        'type' => 'xml',
        'code' => $exitCode
    );
}

/**
 * Executes the interpreter on the specified test
 * @param string $test Path to the test without extension
 * @param string $source Path to the interpreter XML source file
 * @return array out - output text (including stderr), type - xml, code - parser exit code
 */
function runInterpreter(string $test, string $source): array
{
    global $intScript;

    $sh = "python3.8 $intScript --source=$source --input=$test.in 2>&1";
    $output = [];
    $exitCode = 0;

    exec($sh, $output, $exitCode);
    return array(
        'out' => implode("\n", $output),
        'type' => 'text',
        'code' => $exitCode
    );
}

/**
 * Continuously executes the parser and the interpreter
 * @param string $test Path to the test without extension
 * @return array out - output text (including stderr), type - xml, code - parser exit code
 */
function runParserAndInterpreter(string $test): array
{
    global $noclean;

    $xml = runParser($test);
    if ($xml['code'] != 0) {
        return [
            'out' => '',
            'code' => $xml['code']
        ];
    }

    $file = fopen("$test.temp.xml", 'w');
    fwrite($file, $xml['out']);
    fclose($file);

    $out = runInterpreter($test, "$test.temp.xml");

    if (!$noclean) {
        unlink("$test.temp.xml");
    }

    return $out;
}

/**
 * Reads file to end
 * @param string $file Path to file
 * @return string File content
 */
function readFileContent(string $file): string
{
    $fs = fopen($file, 'r');
    $res = "";
    while (!feof($fs))
        $res .= fgets($fs);
    fclose($fs);

    return $res;
}

/**
 * Compares exit codes
 * @param int $outExitCode Received exit code
 * @param string $ref Reference file with the expected exit code
 * @return array success - bool, message - if failed, info message
 */
function compareExitCode(int $outExitCode, string $ref): array
{
    $expected_ec = readFileContent($ref);

    if ((int) $expected_ec == $outExitCode)
        return ['success' => true];
    else
        return [
            'success' => false,
            'message' => "Wrong exit code. Expected $expected_ec but got $outExitCode"
        ];
}

/**
 * Compares XML files using JExamXML
 * @param string $out Received output
 * @param string $ref Reference file
 * @param string $delta Difference file
 * @return array success - bool, message - if failed, info message, expected, actual, difference
 */
function compareXml(string $out, string $ref, string $delta): array
{
    global $jExamXmlPath;
    $sh = "java -jar $jExamXmlPath/jexamxml.jar $out $ref $delta $jExamXmlPath/options";

    $result = exec($sh, result_code: $resultCode);
    if ($resultCode != 0) {
        $outContent = readFileContent($out);
        $refContent = readFileContent($ref);
        $difference = readFileContent($delta);

        return [
            'success' => false,
            'message' => 'XML output is not equal to the reference output',
            'expected' => $refContent,
            'actual' => $outContent,
            'difference' => $difference
        ];
    } else
        return ['success' => true];
}

/**
 * Compares files using diff
 * @param string $out Received output
 * @param string $ref Reference file
 * @return array success - bool, message - if failed, info message, expected, actual, difference
 */
function compareText(string $out, string $ref): array
{
    $sh = "diff $out $ref";

    $result = exec($sh, $execOut);
    $difference = implode("\n", $execOut);
    if ($result != '') {
        $outContent = readFileContent($out);
        $refContent = readFileContent($ref);

        return [
            'success' => false,
            'message' => 'Output is not equal to the reference output',
            'expected' => $refContent,
            'actual' => $outContent,
            'difference' => $difference
        ];
    } else
        return ['success' => true];
}

/**
 * @param string $test Path to the test without extension
 * @return array success - bool, message - if failed, info message, expected, actual, difference
 */
function runTest(string $test): array
{
    global $parseOnly, $intOnly, $noclean;

    if ($parseOnly)
        $out = runParser($test);
    else if ($intOnly)
        $out = runInterpreter($test, "$test.src");
    else
        $out = runParserAndInterpreter($test);

    $result = compareExitCode($out['code'], "$test.rc");
    if (!$result['success'] || $out['code'] != 0) {
        $result['path'] = $test;
        return $result;
    }

    $fs = fopen("$test.temp.out", 'w');
    fwrite($fs, $out['out']);
    fclose($fs);

    if ($parseOnly)
        $result = compareXml("$test.temp.out", "$test.out", "$test.delta");
    else
        $result = compareText("$test.temp.out", "$test.out");

    if (!$noclean) {
        unlink("$test.temp.out");
        if ($parseOnly)
            unlink("$test.delta");
    }

    $result['path'] = $test;
    return $result;
}

/**
 * Generates HTML
 * @param array $results Test results
 * @return string HTML
 */
function generateHTML(array $results): string
{
    $case = 1;
    $failed = 0;
    $testInfo = "";
    foreach ($results as $result) {
        $testInfo .= "<div class=\"test-result\">";
        if ($result['success']) {
            $path = $result['path'];
            $testInfo .= "<p class=\"header\">Test case #$case: <span class=\"success\">success</span></p>
        <p>Path: $path</p>";
        } else {
            $failed += 1;
            $path = $result['path'];
            $message = $result['message'];

            $testInfo .= "<p class=\"header\">Test case #$case: <span class=\"fail\">fail</span></p>
        <p>Path: $path</p>
        <p><b>Message:</b> $message</p>";

            if (key_exists('expected', $result) && key_exists('actual', $result)) {
                $out = $result['actual'];
                $ref = $result['expected'];
                $testInfo .= "<p class=\"header\">Your output</p>
        <textarea readonly>$out</textarea>";
                $testInfo .= "<p class=\"header\">Reference output</p>
        <textarea readonly>$ref</textarea>";
            }

            if (key_exists('difference', $result)) {
                $difference = $result['difference'];
                $testInfo .= "<p class=\"header\">Difference</p>
        <textarea readonly>$difference</textarea>";
            }
        }

        $testInfo .= "</div>";
        $case += 1;
    }

    $total = $case - 1;
    $passed = $total - $failed;
    $header = "<h2>Tests finished: $passed passed, $failed failed, $total total</h2>";

    $html = "<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <title>Testing results</title>
    <style>
        * {
            font-family: Arial, serif;
        }
        main {
            margin-top: 4%;
            margin-left: 20%;
        }
        .test-result {
            margin-bottom: 3%;
            margin-left: 1%;
            margin-right: 1%;
        }
        .test-result > p {
            margin-top: 1%;
        }
        p.header {
            font-weight: bold;
        }
        .success {
            color: green;
        }
        .fail {
            color: red;
        }
        textarea {
            width: 80%;
            height: 200px;
        }
    </style>
</head>
<body>
<main>
    $header
    $testInfo
</main>
</body>
</html>";

    return $html;
}

function main()
{
    global $directory;

    parseArgs();
    $tests = findTestsInFolder($directory);
    $results = [];
    foreach ($tests as $test)
        $results[] = runTest($test);

    $html = generateHTML($results);
    echo "$html\n";
}

try {
    main();
} catch (Error $err) {
    error(ExitCode::INTERNAL_ERROR, "Unexpected error:\n$err");
}

