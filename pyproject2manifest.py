import json
import os
import re

import toml


def get_latest_versions_from_pyproject():
    pyproject_path = "pyproject.toml"
    with open(pyproject_path, "r") as toml_file:
        content = toml.load(toml_file)

    dependencies = (
        content.get("tool", {})
        .get("poetry", {})
        .get("group", {})
        .get("all", {})
        .get("dependencies", {})
    )
    return dependencies


def split_package_version(string):
    match = re.search(r"([a-zA-Z0-9_-]+)([><!=]=?[0-9\.]+.*)", string)
    if match:
        package_name = match.group(1)
        version_constraint = match.group(2)
        return package_name, version_constraint
    else:
        return string, None


def update_manifest_requirements(directory, latest_versions):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == "manifest.json":
                manifest_path = os.path.join(root, file)
                with open(manifest_path, "r+") as manifest_file:
                    manifest_data = json.load(manifest_file)
                    if "requirements" in manifest_data:
                        requirements = manifest_data["requirements"]
                        updated_requirements = []
                        for req in requirements:
                            package_name, version_constraint = split_package_version(
                                req
                            )
                            latest_version = latest_versions.get(package_name)
                            if latest_version and "version" in latest_version:
                                latest_version = latest_version["version"]
                            if latest_version and latest_version != "*":
                                updated_requirements.append(
                                    f"{package_name}{latest_version}"
                                )
                            else:
                                updated_requirements.append(req)
                        manifest_data["requirements"] = updated_requirements
                        manifest_file.seek(0)
                        json.dump(manifest_data, manifest_file, indent=2)
                        manifest_file.truncate()


directory_path = "."
latest_versions = get_latest_versions_from_pyproject()
update_manifest_requirements(directory_path, latest_versions)
print("Manifest files updated with the latest versions.")
