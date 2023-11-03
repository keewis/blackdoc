import argparse
import re

version_re = re.compile(
    r"https://github.com/psf/(?:black|black-pre-commit-mirror)\s+"
    r"rev: (.+)\s+hooks:(?:\s+-id: [-_a-zA-Z0-9]+)*\s+- id: (?:black|black-jupyter)"
)
black_pin_re = re.compile(
    r"(- id: blackdoc.+?additional_dependencies:.+?black==)[.\w]+",
    re.DOTALL,
)


def find_black_version(content):
    match = version_re.search(content)
    if match is None:
        raise ValueError("cannot find the black hook")
    version = match.group(1)
    return version


def update_black_pin(content, version):
    return black_pin_re.sub(rf"\g<1>{version}", content)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()
    with open(args.path) as f:
        content = f.read()

    version = find_black_version(content)
    replaced = update_black_pin(content, version)

    if content != replaced:
        with open(args.path, mode="w") as f:
            f.write(replaced)
        return 1
    else:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
