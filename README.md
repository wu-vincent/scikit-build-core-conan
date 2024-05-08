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

`scikit-build-core-conan` supports a broad range of configuration options. These options can be placed directly in
the `pyproject.toml` file. They can also be passed via `-C/--config-setting` in build or `-C/--config-settings`
in `pip`. Below are the supported configuration options:

```toml
[tool.scikit-build-core-conan]
path = "."
build = "missing"
profile = "default"
options = []
settings = []
config = []
generator = "Ninja"
output_folder = "build"
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
