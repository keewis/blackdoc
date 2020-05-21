import warnings

detection_funcs = {}
extraction_funcs = {}
reformatting_funcs = {}
include_patterns = {}


def register_format(name, obj):
    """ register a new format """
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
