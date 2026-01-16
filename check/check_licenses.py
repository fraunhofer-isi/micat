# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import functools
import logging
import operator
import tomllib
from pathlib import Path
from sys import exit as sysexit

from license_scanner import get_all_licenses
from licensecheck import license_matrix, packageinfo
from licensecheck.types import JOINS, License, PackageInfo, ucstr
from packaging.requirements import Requirement

logger = logging.getLogger(__name__)


def main():
    _initialize_logging()

    ignore_packages = [
        "reuse",  # combined license is not recognized: "Apache-2.0 AND CC0-1.0 AND CC-BY-SA-4.0 AND GPL-3.0-or-later"
        "referencing",  # has MIT license but is not recognized
    ]

    fail_packages = []

    ignore_licenses = [
        # work around for bug in licensecheck for apache
        "APACHE SOFTWARE LICENSE",
        # work around for bug in licensecheck for dual license
        "MIT License;; Academic Free License (AFL)",
    ]

    fail_licenses = []

    # considers all packages from the workspace; only makes sense in the context of
    # continuous integration pipelines/workflow actions (or within virtualenvs)
    licenses_from_license_scanner = get_all_licenses()
    license_lists = licenses_from_license_scanner.values()
    requirements = functools.reduce(operator.iadd, license_lists, [])

    project_license, dependencies = _license_and_dependencies(
        ignore_packages,
        fail_packages,
        ignore_licenses,
        fail_licenses,
        requirements,
    )

    # noinspection PyTypeChecker
    sorted_dependencies = sorted(dependencies)
    output = simple_formatter(project_license, sorted_dependencies)
    logger.info(output)

    is_incompatible = any(not dependency.licenseCompat for dependency in dependencies)
    exit_code = 1 if is_incompatible else 0
    sysexit(exit_code)


def _initialize_logging():
    # Configure logging only if no handlers are set (avoid duplicate handlers when imported)
    if not logging.getLogger().handlers:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.getLogger().setLevel(logging.INFO)


def _license_and_dependencies(
    ignore_packages,
    fail_packages,
    ignore_licenses,
    fail_licenses,
    requirements,
) -> tuple[License, set[PackageInfo]]:
    project_license = _project_license()
    info_manager = packageinfo.PackageInfoManager()
    info_manager.resolve_requirements(
        requirements_paths=["pyproject.toml"],
        groups=[],
        extras=["dev"],
        skip_dependencies=[],
    )

    existing = {pkg.name.lower() for pkg in info_manager.reqs}
    for spec in requirements:
        req = Requirement(spec)
        name = req.name
        if name.lower() in existing:
            continue
        # Construct a minimal placeholder PackageInfo; version left blank
        minimal_package_info = PackageInfo(name=name, version="", errorCode=1)
        info_manager.reqs.add(minimal_package_info)

    packages = info_manager.getPackages()

    for package in packages:
        _check_and_update_compatibility(
            package,
            project_license,
            fail_licenses,
            fail_packages,
            ignore_licenses,
            ignore_packages,
        )
    return project_license, packages


def _check_and_update_compatibility(  # pylint: disable=too-many-arguments
    package,
    project_license,
    fail_licenses,
    fail_packages,
    ignore_licenses,
    ignore_packages,
):
    package_name = package.name.lower()
    is_ignored_package = package_name in [
        package_name.lower() for package_name in ignore_packages
    ]
    is_failing_package = package_name in [
        package_name.lower() for package_name in fail_packages
    ]
    if is_ignored_package:
        package.licenseCompat = True
    elif is_failing_package:
        package.licenseCompat = False
    else:
        package.licenseCompat = license_matrix.depCompatWMyLice(
            project_license,
            license_matrix.licenseType(package.license),
            license_matrix.licenseType(JOINS.join(ignore_licenses)),
            license_matrix.licenseType(JOINS.join(fail_licenses)),
        )
    return package


def _read_project_license_text(pyproject_path: Path = Path("pyproject.toml")) -> str:
    try:
        with pyproject_path.open("rb") as f:
            data = tomllib.load(f)
    except FileNotFoundError as e:  # pragma: no cover - critical failure
        message = "pyproject.toml not found; cannot determine project license"
        raise RuntimeError(message) from e

    project_table = data.get("project", {})
    license_field = project_table.get("license")

    if isinstance(license_field, dict):
        # PEP 621 style
        text = license_field.get("text")
        if text:
            return text
        license_file = license_field.get("file")
        if license_file:
            license_file_path = pyproject_path.parent / license_file
            try:
                return license_file_path.read_text(encoding="utf-8")
            except FileNotFoundError as e:  # pragma: no cover
                message = f"Declared license file '{license_file}' not found next to pyproject.toml"
                raise RuntimeError(message) from e
    elif isinstance(
        license_field, str
    ):  # direct string (less common in modern PEP 621 usage)
        return license_field
    message = "Could not extract project license from pyproject.toml"
    raise RuntimeError(message)


def _project_license():
    # Replaced deprecated: packageinfo.getMyPackageLicense()
    project_license_text: str = _read_project_license_text()
    project_license = license_matrix.licenseType(ucstr(project_license_text))[0]
    return project_license


def simple_formatter(project_license, dependencies):
    lines = [f"Project License: {project_license}"]
    for dep in dependencies:
        status = "✔" if dep.licenseCompat else "✘"
        lines.append(f"{status} {dep.name}: {dep.license}")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
