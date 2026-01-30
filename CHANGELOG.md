# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.9.1] - 2025-01-30

### Changed

- Minimum Python version raised to 3.10

### Fixed

- Fixed `TypeError: Can't convert target list[str]` when using scikit-build-core's SourceChain by removing `from __future__ import annotations` which caused type annotations to be stored as strings at runtime

## [0.9.0] - 2025-01-22

> **Note:** This package will be renamed to `scikit-build-conan` at version 1.0.

### Added

- CI workflow for automated testing
- Support for multiple `build` policy values ([#9](https://github.com/vpenso/scikit-build-core-conan/issues/9))
- Extended `ConanSettings` with additional configuration options

### Changed

- Bumped dependencies: scikit-build-core to 0.11.0, conan to 2.20.0
- Cleaned up optional dependencies

## [0.8.0] - 2024-12-15

### Added

- Ruff linting configuration

### Changed

- Improved handling for host and build-specific settings
- Expanded `ConanSettings` fields
- Updated Python requirement to 3.8+

### Fixed

- Corrected profile options

## [0.7.2] - 2024-10-20

### Fixed

- Build profile handling

## [0.7.1] - 2024-10-15

### Fixed

- Resolved import error for scikit-build-core >= 0.11.4 ([#8](https://github.com/vpenso/scikit-build-core-conan/issues/8))

## [0.7.0] - 2024-09-10

### Fixed

- Resolved build errors caused by functions removed in Conan 2.17.0 ([#2](https://github.com/vpenso/scikit-build-core-conan/issues/2))

## [0.6.0] - 2024-08-01

### Changed

- Split profiles for host and build configurations

### Fixed

- Create default Conan profile if not present

## [0.5.2] - 2024-06-15

### Fixed

- Use Conan API directly instead of Conan CLI

## [0.5.1] - 2024-06-10

### Fixed

- Minor bug fixes

## [0.5.0] - 2024-05-20

### Added

- Activate Conan environment in wheel build

## [0.4.0] - 2024-04-15

### Changed

- Documentation improvements

## [0.3.1] - 2024-03-20

### Fixed

- Added `__future__` annotations import for backwards compatibility

## [0.3.0] - 2024-03-10

### Changed

- Refactored classes into separate modules

## [0.2.1] - 2024-02-25

### Changed

- `detect_profile` is now called regardless of whether a profile is specified

## [0.2.0] - 2024-02-15

### Added

- Support for exporting local recipes before conan install
- `tomli` support for Python versions < 3.11
- Configuration override support

## [0.1.0] - 2024-01-20

### Added

- Initial release
- Basic wrapper for `scikit_build_core.build`
- Configuration via `pyproject.toml`
- CD workflow for automated releases
