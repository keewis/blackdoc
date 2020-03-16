import warnings

detection_funcs = {}
extraction_funcs = {}
reformatting_funcs = {}


def register_format(name, detection_func, extraction_func, reformatting_func):
    """ register a new format """
    if name in detection_funcs:
        warnings.warn(f"{name} already registered", RuntimeWarning)

    detection_funcs[name] = detection_func
    extraction_funcs[name] = extraction_func
    reformatting_funcs[name] = reformatting_func
