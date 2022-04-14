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
    case INTERNAL_ERROR = 99;
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

    if (!file_exists($parseScript) && !$intOnly)
        error(ExitCode::BAD_PATH, "File $parseScript does not exist.");
    if (!file_exists($intScript) && !$parseOnly)
        error(ExitCode::BAD_PATH, "File $intScript does not exist.");
}

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

function findTestsInFolder(string $directory): array
{
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
                checkAndCreateTestFiles($directory, $name);
                $result[] = $directory . '/' . $name;
            }
        }
    }

    return $result;
}

function runParser(string $test): array {
    global $parseScript;

    $sh = "cat $test.src | php8.1 $parseScript"; // todo use merlin command
    $output = [];
    $exitCode = 0;
    exec($sh, $output, $exitCode);
    return array(
        'out' => implode("\n", $output),
        'type' => 'xml',
        'code' => $exitCode
    );
}

function runInterpreter(string $test, string $source): array {
    global $intScript;

    $sh = "python3.8 $intScript --source=$source --input=$test.in"; // todo use merlin command
    $output = [];
    $exitCode = 0;

    exec($sh, $output, $exitCode);
    return array(
        'out' => implode("\n", $output),
        'type' => 'text',
        'code' => $exitCode
    );
}

function runParserAndInterpreter(string $test): array {
    global $noclean;

    $xml = runParser($test);
    if ($xml['code'] != 0) {
        return [
            'success' => false,
            'message' => 'Parsing failed',
            'expected' => 0,
            'actual' => $xml['code']
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

function compareExitCode(string $outExitCode, string $ref): array {
    $fs = fopen($ref, 'r');
    $expected_ec = (int) fread($fs, 8);
    fclose($fs);

    if ($expected_ec == $outExitCode)
        return ['success' => true];
    else
        return [
            'success' => false,
            'message' => 'Wrong exit code',
            'expected' => $expected_ec,
            'actual' => $outExitCode
        ];
}

function readFile(string $file): string {
    $fs = fopen($file, 'r');
    $res = "";
    while ($line = fgets($fs))
        $res .= $line;
    fclose($fs);

    return $res;
}

function compareXml(string $out, string $ref, string $delta): array {
    global $jExamXmlPath;
    $sh = "java -jar $jExamXmlPath/jexamxml.jar $out $ref $delta $jExamXmlPath/options";

    $result = exec($sh);
    if (str_contains($result, "not identical"))
    {
        $outContent = readFile($out);
        $refContent = readFile($ref);
        $difference = readFile($delta);

        return [
            'success' => false,
            'message' => 'XML output is not equal to the reference output',
            'expected' => $refContent,
            'actual' => $outContent,
            'difference' => $difference
        ];
    }
    else
        return ['success' => true];
};

function compareText(string $out, string $ref): array {
    $sh = "diff $out $ref";

    $result = exec($sh, $execOut);
    $difference = implode("\n", $execOut);
    if ($result != '') {
        $outContent = readFile($out);
        $refContent = readFile($ref);

        return [
            'success' => false,
            'message' => 'Output is not equal to the reference output',
            'expected' => $refContent,
            'actual' => $outContent,
            'difference' => $difference
        ];
    }
    else
        return ['success' => true];
}

function runTest(string $test): array {
    global $parseOnly, $intOnly, $noclean;

    if ($parseOnly)
        $out = runParser($test);
    else if ($intOnly)
        $out = runInterpreter($test, "$test.src");
    else
        $out = runParserAndInterpreter($test);

    $result = compareExitCode($out['code'], "$test.rc");
    if (!$result['success'])
    {
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

function generateHTML(array $results): string {
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
    <h1>Test results</h1>";

    $case = 1;
    foreach ($results as $result) {
        $html .= "<div class=\"test-result\">";

        if ($result['success']) {
            $path = $result['path'];
            $html .= "<p class=\"header\">Test case #$case: <span class=\"success\">success</span></p>
        <p>Path: $path</p>";
        } else {
            $path = $result['path'];
            $message = $result['message'];
            $difference = $result['difference'];

            $html .= "<p class=\"header\">Test case #$case: <span class=\"fail\">fail</span></p>
        <p>Path: $path</p>
        <p><b>Message:</b> $message</p>
        <p class=\"header\">Difference</p>
        <textarea readonly>$difference</textarea>";
        }

        $html .= "</div>";
        $case += 1;
    }

    $html .= "</main>
</body>
</html>";
    return $html;
}

function main() {
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

