# scikit-build-core-conan

A conan plugin for scikit-build-core

> [!NOTE]
> This project is under early development. Should you encounter any problems, please feel free to open an issue.

## Example

To use `scikit-build-core-conan`, add it to your `build-system.requires`, and specify the `scikit_build_core_conan.build` 
builder as your `build-system.build-backend`. You do not need to specify `scikit_build_core`.

```toml

[build-system]
requires = ["scikit-build-core-conan"]
build-backend = "scikit_build_core_conan.build"

[project]
name = "scikit_build_conan_simplest"
version = "0.0.1"
```

## Configuration

All configuration options can be placed in `pyproject.toml`, passed via `-C/--config-setting` in build or 
`-C/--config-settings` in `pip`. The defaults are listed below:

```toml
[tool.scikit-build-core-conan]
path = "."
build = "missing"
profile = ""
options = []
settings = []
config = []
generator = ""
output_folder = ""
```
