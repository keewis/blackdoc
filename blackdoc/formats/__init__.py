import textwrap

from . import doctest, none
from .register import detection_funcs  # noqa
from .register import extraction_funcs, reformatting_funcs, register_format


def extract_code(line_unit, category):
    dedented = textwrap.dedent(line_unit)
    indentation_depth = line_unit.find(dedented[:5])

    func = extraction_funcs.get(category, None)
    if func is None:
        raise RuntimeError(f"unknown code format: {category}")

    prompt_length, extracted = func(dedented)
    return indentation_depth, prompt_length, extracted


def reformat_code(line_unit, category, indentation_depth):
    func = reformatting_funcs.get(category, None)
    if func is None:
        raise RuntimeError(f"unknown code format: {category}")

    reformatted = func(line_unit)

    return textwrap.indent(reformatted, " " * indentation_depth)


for module in (none, doctest):
    name = module.__name__.split(".")[-1]
    register_format(name, module)
