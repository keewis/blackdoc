import warnings

import more_itertools

detection_funcs = {}
extraction_funcs = {}
reformatting_funcs = {}
include_patterns = {}


def format_include_patterns():
    patterns = set(include_patterns.values())
    joined_patterns = "|".join(patterns)

    if "|" not in joined_patterns:
        return joined_patterns
    else:
        return f"({joined_patterns})"


def disable(format_names):
    names = tuple(more_itertools.always_iterable(format_names))
    unknown_names = tuple(name for name in names if name not in detection_funcs)
    if any(unknown_names):
        raise ValueError(f"unknown formats: {','.join(unknown_names)}")

    for name in names:
        del detection_funcs[name]


def register_format(name, obj):
    """register a new format"""
    if name in detection_funcs:
        warnings.warn(f"{name} already registered", RuntimeWarning)

    detection_func = getattr(obj, "detection_func")
    extraction_func = getattr(obj, "extraction_func")
    reformatting_func = getattr(obj, "reformatting_func")
    include_pattern = getattr(obj, "include_pattern", None)

    detection_funcs[name] = detection_func
    extraction_funcs[name] = extraction_func
    reformatting_funcs[name] = reformatting_func

    if include_pattern is not None:
        include_patterns[name] = include_pattern
