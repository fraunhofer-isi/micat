# © 2023 - 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from sys import exit as sysexit

from license_scanner import get_all_licenses
from licensecheck import formatter, get_deps, license_matrix, packageinfo
from licensecheck.types import JOINS, License, PackageInfo


def main():
    using = 'PEP631'
    ignore_packages = ['reuse']  # work around for bug in licensecheck for multiple licenses
    fail_packages = []
    ignore_licenses = [
        # work around for bug in licensecheck for apache
        'Apache Software License',
        # not know by licensecheck, yet
        'Zope Public License',
        # work around for bug in licensecheck for multiple licenses
        'MIT License;; Academic Free License (AFL)',
    ]
    fail_licenses = []

    is_using_license_scanner = True
    if is_using_license_scanner:
        # considers all packages from the workspace; only makes sense in the context of
        # continuous integration pipelines/workflow actions (or within virtualenvs)
        licenses_from_license_scanner = get_all_licenses()
        requirements = sum(licenses_from_license_scanner.values(), [])
    else:
        # only considers direct dependencies
        requirements = get_deps.getReqs(using)

    project_license, dependencies = _license_and_dependencies(
        using,
        ignore_packages,
        fail_packages,
        ignore_licenses,
        fail_licenses,
        requirements
    )

    ansi_format = formatter.formatMap['ansi']
    # noinspection PyTypeChecker
    sorted_dependencies = sorted(dependencies)
    output = ansi_format(project_license, sorted_dependencies)
    print(output)

    is_incompatible = any(not dependency.licenseCompat for dependency in dependencies)
    exit_code = 1 if is_incompatible else 0
    sysexit(exit_code)


def _license_and_dependencies(  # pylint: disable=too-many-arguments
    using: str,
    ignore_packages: list[str],
    fail_packages: list[str],
    ignore_licenses: list[str],
    fail_licenses: list[str],
    requirements: set[str] = None
) -> tuple[License, set[PackageInfo]]:
    if requirements is None:
        requirements = get_deps.getReqs(using)

    project_license = _project_license()
    packages = packageinfo.getPackages(requirements)

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
    is_ignored_package = package_name in [package_name.lower() for package_name in ignore_packages]
    is_failing_package = package_name in [package_name.lower() for package_name in fail_packages]
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


def _project_license():
    project_license_text = packageinfo.getMyPackageLicense()
    project_license = license_matrix.licenseType(project_license_text)[0]
    return project_license


if __name__ == '__main__':
    main()
