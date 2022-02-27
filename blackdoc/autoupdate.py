import argparse

import rich.console
from rich.syntax import Syntax

console = rich.console.Console()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=argparse.FileType())
    args = parser.parse_args()
    content = args.file.read()
    console.print(Syntax(content, "yaml"))

    raise SystemExit(1)
