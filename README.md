# scikit-build-core-conan

A conan plugin for scikit-build-core

> [!NOTE]
> This project is under early development. Should you encounter any problems, please feel free to open an issue.

## Installation

```shell
pip install scikit-build-core-conan
```

To use `scikit-build-core-conan`, add it to your `build-system.requires`, and specify
the `scikit_build_core_conan.build` builder as your `build-system.build-backend`. You do not need to
specify `scikit_build_core` as it will be required automatically.

## Project Example

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

All configuration These options can be placed directly in the `pyproject.toml` file. They can also be passed via
`-C/--config-setting` in build or `-C/--config-settings` in `pip`.

A quick summary and some defaults are listed below:

```toml
[tool.scikit-build-core-conan]
# Path to a folder containing a recipe (conanfile.py or conanfile.txt)
path = "."

# Specify which packages to build from source
build = "missing"

# Look in the specified remote or remotes server. Leave it empty will use all remotes.
remote = []

# Do not use remote, resolve exclusively in the cache
no-remote = false

# Apply the specified profile to the host (default) context
profile = ""

# Apply the specified profile to the build context
profile-build = ""

# Apply the specified profile to both contexts
profile-all = ""

# Apply the specified options to the host (default) context
options = []

# Apply the specified options to the build context
options-build = []

# Apply the specified options to both contexts
options-all = []

# Apply the specified settings to the host (default) context
settings = []

# Apply the specified settings to the build context
settings-build = []

# Apply the specified settings to both contexts
settings-all = []

# Apply the specified config to the host (default) context
config = []

# Apply the specified config to the build context
config-build = []

# Apply the specified config to both contexts
config-all = []

# Generators to use (e.g. Ninja)
generator = ""

# The root output folder for generated and build files
output-folder = ""
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
[documentation](https://scikit-build-core.readthedocs.io/en/latest/configuration.html#overrides) of `scikit-build-core`.

For example:

```toml
[[tool.scikit-build-core-conan.overrides]]
if.platform-system = "linux"
profile = "/path/to/profile"
```

## Projects using this build backend:

- **[endstone](https://github.com/EndstoneMC/endstone)**: A high-level plugin api for Minecraft: Bedrock Edition
  Dedicated Servers.
