import json
import os
import re

import toml


def extract_requirements_from_manifests(directory):
    requirements = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == "manifest.json":
                manifest_path = os.path.join(root, file)
                with open(manifest_path, "r") as manifest_file:
                    manifest_data = json.load(manifest_file)
                    if "requirements" in manifest_data:
                        requirements.extend(manifest_data["requirements"])
    return requirements


def split_package_version(string):
    match = re.search(r"([a-zA-Z0-9_-]+)([><!=]=?[0-9\.]+.*)", string)
    if match:
        package_name = match.group(1)
        version_constraint = match.group(2)
        return package_name, version_constraint
    else:
        return string, "*"


def update_pyproject_toml(dependencies):
    pyproject_path = "pyproject.toml"
    with open(pyproject_path, "r") as toml_file:
        content = toml.load(toml_file)

    if "tool" not in content:
        content["tool"] = {}
    if "poetry" not in content["tool"]:
        content["tool"]["poetry"] = {}
    if "group" not in content["tool"]["poetry"]:
        content["tool"]["poetry"]["group"] = {}
    if "all" not in content["tool"]["poetry"]["group"]:
        content["tool"]["poetry"]["group"]["all"] = {"optional": True}

    content["tool"]["poetry"]["group"]["all"]["dependencies"] = {}

    for dep in dependencies:
        pkg_name, pkg_version = split_package_version(dep)
        content["tool"]["poetry"]["group"]["all"]["dependencies"][
            pkg_name
        ] = pkg_version

    content["tool"]["poetry"]["group"]["all"]["dependencies"] = dict(
        sorted(content["tool"]["poetry"]["group"]["all"]["dependencies"].items())
    )

    with open(pyproject_path, "w") as toml_file:
        toml.dump(content, toml_file)


directory_path = "FHEM/bindings/python"
all_requirements = extract_requirements_from_manifests(directory_path)

update_pyproject_toml(all_requirements)
print("Requirements added to pyproject.toml.")
