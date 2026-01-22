# scikit-build-core-conan

A conan plugin for scikit-build-core

## Example

To use `scikit-build-core-conan`, add it to your `build-system.requires`, and specify
the `scikit_build_core_conan.build` builder as your `build-system.build-backend`. You do not need to
specify `scikit_build_core` as it will be required automatically.

Here's a simple example on how you can use `scikit-build-core-conan` in your `pyproject.toml`.

```toml
[build-system]
requires = ["scikit-build-core-conan"]
build-backend = "scikit_build_core_conan.build"

[project]
name = "scikit_build_conan_simplest"
version = "0.0.1"
```

## Configuration

All options can be placed directly in `pyproject.toml` under `[tool.scikit-build-core-conan]`. They can also be passed
via `-C/--config-setting` in build or `-C/--config-settings` in pip.

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

### Local recipes

Sometimes you may want to consume a local recipe rather than from the conan centre index. You can do this like this:

```toml
[[tool.scikit-build-core-conan.local-recipes]]
path = "path/to/recipe"
name = "recipe"   # optional: package name if not specified in conanfile
version = "0.0.1" # optional: package version if not specified in conanfile
```

### Overrides

`scikit-build-core-conan` uses the same override system as `scikit-build-core`. For more details, check out the
[documentation](https://scikit-build-core.readthedocs.io/en/latest/configuration/overrides.html) of `scikit-build-core`.

For example:

```toml
[[tool.scikit-build-core-conan.overrides]]
if.platform-system = "linux"
profile = "path/to/profile"
```

## Projects using this build backend:

- **[endstone](https://github.com/EndstoneMC/endstone)**: A high-level plugin api for Minecraft: Bedrock Edition
  Dedicated Servers.
