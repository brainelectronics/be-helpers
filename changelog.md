# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--
## [x.y.z] - yyyy-mm-dd
### Added
### Changed
### Removed
### Fixed
-->
<!--
RegEx for release version from file
r"^\#\# \[\d{1,}[.]\d{1,}[.]\d{1,}\] \- \d{4}\-\d{2}-\d{2}$"
-->

## Released
## [0.1.0] - 2022-08-08
### Added
- This changelog file
- [`.coveragerc`](.coveragerc) file
- [`.flake8`](.flake8) file
- [`.gitignore`](.gitignore) file bases on latest
  [Python gitignore template][ref-python-gitignore-template]
- Default [workflows](.github/workflows)
- Script to [create report directories](create_report_dirs.py)
- [`unittest.cfg`](tests/unittest.cfg) file
- [`requirements.txt`](requirements.txt) file to setup required packages
- Initial [`be-helpers`](src/be-helpers) package
- Initial root [`README`](README.md)
- [`setup.py`](setup.py) and [`setup.cfg`](setup.cfg) file
- [`tox.ini`](tox.ini) file using `nose2` and `coverage` create coverage report

<!-- Links -->
[Unreleased]: https://github.com/brainelectronics/be-helpers/compare/0.1.0...develop

[0.1.0]: https://github.com/brainelectronics/be-helpers/tree/0.1.0

<!--
[ref-issue-1]: https://github.com/brainelectronics/be-helpers/issues/1
-->

[ref-python-gitignore-template]: https://github.com/github/gitignore/blob/e5323759e387ba347a9d50f8b0ddd16502eb71d4/Python.gitignore
