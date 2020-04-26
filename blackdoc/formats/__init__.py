import textwrap

from . import doctest, ipython, none, rst
from .register import detection_funcs  # noqa
from .register import extraction_funcs, reformatting_funcs, register_format


def extract_code(line_unit, code_format):
    dedented = textwrap.dedent(line_unit)
    indentation_depth = line_unit.find(dedented[:5])

    func = extraction_funcs.get(code_format, None)
    if func is None:
        raise RuntimeError(f"unknown code format: {code_format}")

    parameters, extracted = func(dedented)
    return indentation_depth, parameters, extracted


def reformat_code(line_unit, code_format, indentation_depth, **parameters):
    func = reformatting_funcs.get(code_format, None)
    if func is None:
        raise RuntimeError(f"unknown code format: {code_format}")

    reformatted = func(line_unit, **parameters)

    return textwrap.indent(reformatted, " " * indentation_depth)


for module in (none, doctest, ipython, rst):
    register_format(module.name, module)
