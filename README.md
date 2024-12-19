<!--
© 2024 Fraunhofer-Gesellschaft e.V., München

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# MICAT

[**MICAT**](https://micatool.eu) – **M**ultiple **I**mpacts **C**alculation **T**ool – is a project that develops a comprehensive approach to estimate Multiple Impacts of Energy Efficiency (MI-EE) by co-creating a free, easy-to-use, scientifically sound online tool.

For more **open source** software provided by [**Fraunhofer ISI**](https://www.isi.fraunhofer.de/) see https://github.com/fraunhofer-isi.

## Documentation

* Online: https://fraunhofer-isi.github.io/micat
* As *.pdf: https://fraunhofer-isi.github.io/micat/latex/micat.pdf
* Project: https://micatool.eu
* Front-end: https://github.com/fraunhofer-isi/micat-vue

## Usage

Install dependencies with

```
pip install .[dev]
```

Start MICAT back-end with

```
cd src/micat
python main.py ./data/confidential_dummy.sqlite
```

Open a browser and enter some API route, for example

```
http://localhost:5000/id_region
```

You might want to adapt the

* dummy values in the databse "confidential_dummy.sqlite" and the
* default data in src/micat/date/public.sqlite

to your needs.

For informations about the front-end see [micat-vue](https://github.com/fraunhofer-isi/micat-vue)

## Badges

Click on some badge to navigate to the corresponding **quality assurance** workflow:

### Documentation

[![doc](https://github.com/fraunhofer-isi/micat/actions/workflows/doc.yml/badge.svg)](https://github.com/fraunhofer-isi/micat/actions/workflows/doc.yml) Generates documentation with [Sphinx](https://www.sphinx-doc.org/)

### Formatting & linting

[![lint](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/fhg-isi/4bb6f7ce335564341b0181db14bdc98f/raw/micat_lint.json)](https://github.com/fraunhofer-isi/micat/actions/workflows/lint.yml) Checks code formatting with [Pylint](https://pylint.readthedocs.io/)

### Test coverage

[![coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/fhg-isi/4bb6f7ce335564341b0181db14bdc98f/raw/micat_coverage.json)](https://github.com/fraunhofer-isi/micat/actions/workflows/coverage.yml) Determines test coverage with [pytest-cov](https://github.com/pytest-dev/pytest-cov)

### License compliance

[![license_check](https://github.com/fraunhofer-isi/micat/actions/workflows/license_check.yml/badge.svg)](https://github.com/fraunhofer-isi/micat/actions/workflows/license_check.yml) Checks license compatibility with [LicenseCheck](https://github.com/FHPythonUtils/LicenseCheck)

[![reuse_annotate](https://github.com/fraunhofer-isi/micat/actions/workflows/reuse_annotate.yml/badge.svg)](https://github.com/fraunhofer-isi/micat/actions/workflows/reuse_annotate.yml) Creates copyright & license annotations with [reuse](https://git.fsfe.org/reuse/tool)

[![reuse compliance](https://api.reuse.software/badge/github.com/fraunhofer-isi/micat)](https://api.reuse.software/info/github.com/fraunhofer-isi/micat) Checks for REUSE compliance with [reuse](https://git.fsfe.org/reuse/tool)

### Dependency updates & security checks

[![renovate](https://github.com/fraunhofer-isi/micat/actions/workflows/renovate.yml/badge.svg)](https://github.com/fraunhofer-isi/micat/actions/workflows/renovate.yml) Updates dependencies with [renovate](https://github.com/renovatebot/renovate)

[![CodeQL](https://github.com/fraunhofer-isi/micat/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/fraunhofer-isi/micat/actions/workflows/github-code-scanning/codeql) Discovers vulnerabilities with [CodeQL](https://codeql.github.com/)

## Licenses

This project is free and open source software:

* It is licensed under the GNU Affero General Public License v3 or later (AGPLv3+) - see [LICENSE](./LICENSES/AGPL-3.0-or-later.txt).
* It uses third-party open source modules, see 
  * [pyproject.toml](./pyproject.toml)
  * [THIRDPARTY.md](./THIRDPARTY.md)

## Notes

<p><a href="https://www.isi.fraunhofer.de/en/publishing-notes.html">PUBLISHING NOTES</a></p>

This project has received funding from the European Union’s Horizon 2020  research and innovation programme under grant agreement No. 101000132.

<img src="https://raw.githubusercontent.com/fraunhofer-isi/.github/refs/heads/main/eu_flag.jpg" alt="eu_flag" width="100px"/> 

