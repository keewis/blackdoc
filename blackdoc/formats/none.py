import more_itertools

name = "none"


def detection_func(lines):
    number, line = more_itertools.first(lines)
    return (number, number + 1), name, line


def extraction_func(line):
    return {}, line


def reformatting_func(line):
    return line
