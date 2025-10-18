import datetime
import difflib


def unified_diff(a, b, path):
    then = datetime.datetime.fromtimestamp(path.stat().st_mtime, datetime.UTC)
    now = datetime.datetime.now(datetime.UTC)
    src_name = f"{path}\t{then} +0000"
    dst_name = f"{path}\t{now} +0000"

    diff = "\n".join(
        difflib.unified_diff(
            a.splitlines(),
            b.splitlines(),
            fromfile=src_name,
            tofile=dst_name,
            lineterm="",
        )
    )

    return diff
