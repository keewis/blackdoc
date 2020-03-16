import more_itertools

from .formats import detection_funcs


def classify(lines):
    lines = more_itertools.peekable(lines)
    while lines:
        maybe_detected = (
            (name, func(lines))
            for name, func in detection_funcs.items()
            if name != "none"
        )
        detected = {name: value for name, value in maybe_detected if value is not None}

        if not detected:
            yield detection_funcs["none"](lines)
        elif len(detected) > 1:
            raise RuntimeError(
                f"cannot classify line: {', '.join(detected.values())} claim it: {lines.peek()}"
            )
        else:
            yield more_itertools.one(detected.values())


def unclassify(labelled_lines):
    for _, line in labelled_lines:
        yield line
