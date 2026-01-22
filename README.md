# scikit-build-core-conan

[![CI](https://github.com/wu-vincent/scikit-build-core-conan/actions/workflows/ci.yml/badge.svg)](https://github.com/wu-vincent/scikit-build-core-conan/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/scikit-build-core-conan)](https://pypi.org/project/scikit-build-core-conan/)
[![Python versions](https://img.shields.io/pypi/pyversions/scikit-build-core-conan)](https://pypi.org/project/scikit-build-core-conan/)
[![License](https://img.shields.io/pypi/l/scikit-build-core-conan)](https://github.com/wu-vincent/scikit-build-core-conan/blob/main/LICENSE)

A [Conan](https://conan.io/) plugin for [scikit-build-core](https://github.com/scikit-build/scikit-build-core) that
simplifies building Python extensions with C/C++ dependencies managed by Conan.

**Why use this?** Instead of manually configuring Conan and CMake toolchains, this plugin handles dependency resolution,
build configuration, and CMake integration automatically - all configured through your `pyproject.toml`.

## Features

- **Seamless Conan 2.x integration** with scikit-build-core's modern Python build system
- **Local recipe support** for consuming in-development Conan packages
- **Lockfile support** for reproducible builds across environments
- **Full configuration via `pyproject.toml`** - no separate Conan commands needed

## Quick Start

Add `scikit-build-core-conan` to your `build-system.requires` and specify `scikit_build_core_conan.build` as your build
backend. You do not need to include `scikit-build-core` separately - it is required automatically.

```toml
[build-system]
requires = ["scikit-build-core-conan"]
build-backend = "scikit_build_core_conan.build"

[project]
name = "my_project"
version = "0.0.1"
```

With this configuration, the plugin will:

1. Look for a `conanfile.py` or `conanfile.txt` in your project root
2. Install dependencies using Conan (building from source if needed)
3. Configure CMake with the appropriate toolchain
4. Build your Python extension

## Configuration

All options can be placed in `pyproject.toml` under `[tool.scikit-build-core-conan]`, or passed via
`-C/--config-setting` in build or `-C/--config-settings` in pip.

```toml
[tool.scikit-build-core-conan]
# Path to a folder containing a recipe (conanfile.py or conanfile.txt)
path = "."

# Specify which packages to build from source. Possible values: "never", "missing", "cascade", ["pattern", ...]
build = "missing"
# Generators to use
generator = ""
# The root output folder for generated and build files
output-folder = ""
# Deploy using the provided deployer to the output folder. Built-in deployers: full_deploy, direct_deploy, runtime_deploy
deployer = []
# Deployer output folder, base build folder by default if not set
deployer-folder = ""
# Execute the deploy() method of the packages matching the provided patterns
deployer-package = []

# Look in the specified remote or remotes server
remote = []
# Do not use remote, resolve exclusively in the cache
no-remote = false
# Will install newer versions and/or revisions in the local cache
update = false

# Apply the specified profile to the host context
profile = ""
# Apply the specified profile to the build context
profile-build = ""
# Apply the specified profile to both contexts at once
profile-all = ""
# Apply the specified options to the host context. Example: ["pkg/*:with_qt=True"]
options = []
# Apply the specified options to the build context
options-build = []
# Apply the specified options to both contexts at once
options-all = []
# Apply the specified settings to the host context. Example: ["compiler=gcc"]
settings = []
# Apply the specified settings to the build context
settings-build = []
# Apply the specified settings to both contexts at once
settings-all = []
# Apply the specified conf to the host context. Example: ["tools.cmake.cmaketoolchain:generator=Xcode"]
config = []
# Apply the specified conf to the build context
config-build = []
# Apply the specified conf to both contexts at once
config-all = []

# Provide a package name if not specified in conanfile
name = ""
# Provide a package version if not specified in conanfile
version = ""
# Provide a user if not specified in conanfile
user = ""
# Provide a channel if not specified in conanfile
channel = ""

# Path to a lockfile. Use "" to avoid automatic use of existing conan.lock file
lockfile = ""
# Do not raise an error if some dependency is not found in lockfile
lockfile-partial = false
# Filename of the updated lockfile
lockfile-out = ""
# Remove unused entries from the lockfile
lockfile-clean = false
```

### Local Recipes

Sometimes you may want to consume a local recipe rather than from the Conan Center Index. You can do this like this:

```toml
[[tool.scikit-build-core-conan.local-recipes]]
path = "path/to/recipe"
name = "recipe"   # optional: package name if not specified in conanfile
version = "0.0.1" # optional: package version if not specified in conanfile
```

### Overrides

`scikit-build-core-conan` uses the same override system as `scikit-build-core`. For more details, check out
the [documentation](https://scikit-build-core.readthedocs.io/en/latest/configuration/overrides.html) of
`scikit-build-core`.

For example:

```toml
[[tool.scikit-build-core-conan.overrides]]
if.platform-system = "linux"
profile = "path/to/profile"
```

## Projects Using This Build Backend

- **[endstone](https://github.com/EndstoneMC/endstone)**: A high-level plugin API for Minecraft: Bedrock Edition
  Dedicated Servers.

*Using scikit-build-core-conan in your project? Feel free to open a PR to add it here!*

## Roadmap

This project will be renamed to `scikit-build-conan` upon the 1.0 stable release.

## Links

- [Changelog](CHANGELOG.md)
- [scikit-build-core documentation](https://scikit-build-core.readthedocs.io/)
- [Conan documentation](https://docs.conan.io/)
- [Report issues](https://github.com/wu-vincent/scikit-build-core-conan/issues)
