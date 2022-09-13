import argparse
import re

version_re = re.compile(r"black\s+rev: (.+)\s+hooks:\s+- id: black")
black_pin_re = re.compile(
    r"(- id: blackdoc.+?additional_dependencies:.+?black==)[.\w]+",
    re.DOTALL,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()
    with open(args.path) as f:
        content = f.read()

    match = version_re.search(content)
    if match is None:
        raise ValueError("cannot find the black hook")
    version = match.group(1)
    replaced = black_pin_re.sub(rf"\g<1>{version}", content)

    if content != replaced:
        with open(args.path, mode="w") as f:
            f.write(replaced)
        return 1
    else:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
