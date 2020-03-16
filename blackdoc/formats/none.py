import more_itertools


def detection_func(lines):
    number, line = more_itertools.first(lines)
    return (number, number + 1), line


def extraction_func(line):
    return 0, line


def reformatting_func(line, indentation_depth):
    return line
