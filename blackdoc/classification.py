import more_itertools

from blackdoc.formats import detection_funcs


def detect_format(lines):
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
            formatted_match_names = ", ".join(sorted(detected.keys()))
            raise RuntimeError(
                "cannot detect code format for line:"
                f" it is claimed by {formatted_match_names}: {lines.peek()}"
            )
        else:
            yield more_itertools.one(detected.values())
