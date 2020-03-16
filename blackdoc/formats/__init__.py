import textwrap

from .register import detection_funcs  # noqa
from .register import extraction_funcs, reformatting_funcs, register_format


def extract_code(line_unit, category):
    dedented = textwrap.dedent(line_unit)
    indentation_level = line_unit.find(dedented[:5])

    func = extraction_funcs.get(category, None)
    if func is None:
        raise RuntimeError(f"unknown code format: {category}")

    return indentation_level, func(dedented)


def reformat_code(line_unit, category, indentation_depth):
    func = reformatting_funcs.get(category, None)
    if func is None:
        raise RuntimeError(f"unknown code format: {category}")

    reformatted = func(line_unit)

    return textwrap.indent(reformatted, " " * indentation_depth)


for module in ():
    register_format(module.__name__, module)
