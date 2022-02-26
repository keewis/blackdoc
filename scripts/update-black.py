import difflib

import more_itertools
import requests
import rich.console
import rich.syntax
import typer
import yaml
from packaging.requirements import Requirement
from packaging.version import Version

console = rich.console.Console()

url_template = "https://api.github.com/repos/{repository}/releases"
repositories = {
    "black": "psf/black",
}


def fetch_json(url):
    return requests.get(url).json()


def update_dependencies(hook, requirements):
    if "additional_dependencies" not in hook:
        return hook
    elif not requirements:
        return hook

    hook = hook.copy()
    deps = hook["additional_dependencies"]
    hook_requirements = {req.name: req for req in (Requirement(dep) for dep in deps)}
    for req in requirements:
        if req.name not in hook_requirements:
            continue
        hook_requirements[req.name] = req
    updated_deps = [str(req) for req in hook_requirements.values()]
    hook["additional_dependencies"] = updated_deps
    return hook


def filter_releases(requirement, releases):
    if not releases:
        return requirement

    specifier = more_itertools.one(requirement.specifier)
    current_version = Version(specifier.version)
    versions = [version for version in releases if version >= current_version]

    potential_requirements = [
        Requirement(f"{requirement.name}{specifier.operator}{version}")
        for version in sorted(versions, reverse=True)
    ]
    if len(potential_requirements) == 0:
        raise ValueError(
            f"none of the fetched releases for '{requirement.name}' matches"
        )

    return more_itertools.first(potential_requirements)


def statistics(old, new):
    total = len(old)
    changed = len([n for o, n in zip(old, new) if o != n])

    return {"changed": changed, "unchanged": total - changed}


def format_statistics(stats, mode):
    templates = {
        "diff": {
            "changed": "[blue]{} hooks[/] [bold]would be changed[/]",
            "unchanged": "[blue]{} hooks[/] would be left unchanged",
        },
        "update": {
            "changed": "[blue]{} hooks[/] [bold]changed[/]",
            "unchanged": "[blue]{} hooks[/] left unchanged",
        },
    }
    template = templates[mode]
    return ", ".join(
        [template[item].format(value) for item, value in stats.items() if value > 0]
    )


def main(path: str, diff: bool = False):
    with open(path) as f:
        data = f.read()
    hooks = yaml.safe_load(data)

    requirements = {
        hook["id"]: [
            Requirement(dep) for dep in hook.get("additional_dependencies", [])
        ]
        for hook in hooks
    }

    urls = {
        name: url_template.format(repository=repository)
        for name, repository in repositories.items()
    }
    release_data = {name: fetch_json(url) for name, url in urls.items()}
    releases = {
        name: [Version(release.get("tag_name")) for release in data]
        for name, data in release_data.items()
    }

    new_requirements = {
        id_: [filter_releases(req, releases.get(req.name, [])) for req in reqs]
        for id_, reqs in requirements.items()
    }
    new_hooks = [
        update_dependencies(hook, new_requirements.get(hook["id"], []))
        for hook in hooks
    ]

    dumped = yaml.safe_dump(
        new_hooks,
        indent=2,
        sort_keys=False,
    )

    stats = statistics(hooks, new_hooks)

    if diff:
        if stats["changed"]:
            diff = "\n".join(
                difflib.unified_diff(
                    data.splitlines(),
                    dumped.splitlines(),
                    fromfile=path,
                    tofile=path,
                    lineterm="",
                )
            )
            console.print(rich.syntax.Syntax(diff, "diff"))
        console.print(format_statistics(stats, mode="diff"))
    else:
        with open(path, mode="w") as f:
            f.write(dumped)
        console.print(format_statistics(stats, mode="update"))

    error_code = int(stats["changed"] != 0)
    raise typer.Exit(code=error_code)


if __name__ == "__main__":
    typer.run(main)
