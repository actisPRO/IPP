from enum import Enum


class ExitCode(Enum):
    OK = 0
    MISSING_ARGUMENT = 10
    READ_ERROR = 11
    UNEXPECTED_XML = 32
