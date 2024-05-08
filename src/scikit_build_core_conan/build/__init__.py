import copy
import dataclasses
import io
import json
import os
import shutil
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from typing import List, Optional

if sys.version_info < (3, 11):
    import tomli as tomllib
else:
    import tomllib

import scikit_build_core.build
from conan.api.conan_api import ConanAPI
from conan.cli.cli import Cli as ConanCli
from scikit_build_core.build import (
    build_sdist,
    get_requires_for_build_editable,
    get_requires_for_build_sdist,
    get_requires_for_build_wheel,
    prepare_metadata_for_build_editable,
    prepare_metadata_for_build_wheel,
)
from scikit_build_core.settings.skbuild_read_settings import SettingsReader, process_overides

__all__ = [
    "build_editable",
    "build_sdist",
    "build_wheel",
    "get_requires_for_build_editable",
    "get_requires_for_build_sdist",
    "get_requires_for_build_wheel",
    "prepare_metadata_for_build_editable",
    "prepare_metadata_for_build_wheel",
]

from scikit_build_core.settings.sources import SourceChain, TOMLSource


@dataclasses.dataclass
class ConanLocalRecipesSettings:
    path: str = "."
    name: Optional[str] = None
    version: Optional[str] = None


@dataclasses.dataclass
class ConanSettings:
    path: str = "."
    build: str = "missing"
    profile: Optional[str] = None
    options: List[str] = dataclasses.field(default_factory=list)
    settings: List[str] = dataclasses.field(default_factory=list)
    config: List[str] = dataclasses.field(default_factory=list)
    generator: Optional[str] = None
    output_folder: Optional[str] = None
    local_recipes: List[ConanLocalRecipesSettings] = dataclasses.field(default_factory=list)


def detect_profile():
    f = io.StringIO()
    conan_api = ConanAPI()
    conan_cli = ConanCli(conan_api)
    with redirect_stdout(f):
        conan_cli.run(["profile", "list", "--format=json"])
    profiles: list[str] = json.loads(f.getvalue())
    if "default" not in profiles:
        conan_cli.run(["profile", "detect"])


def conan_export_local_recipes(settings: ConanLocalRecipesSettings) -> None:
    path = os.path.abspath(settings.path)
    cmd = ["export", f"{path}"]

    if settings.name:
        cmd += ["--name", settings.name]

    if settings.version:
        cmd += ["--version", settings.version]

    conan_api = ConanAPI()
    conan_cli = ConanCli(conan_api)
    conan_cli.run(cmd)


def conan_install(settings: ConanSettings, build_type: str) -> dict:
    path = Path(settings.path).absolute()

    # Use a tmp folder for conanfile to avoid modifying the existing CMakeUserPresets.json
    with tempfile.TemporaryDirectory() as tmp:
        for file in ["conanfile.txt", "conanfile.py"]:
            if (path / file).exists():
                shutil.copy(path / file, tmp)
                break

        cmd = [
            "install",
            f"{tmp}",
            f"--build={settings.build}",
            "-s",
            f"build_type={build_type}",
            "--format=json",
        ]
        if settings.profile:
            cmd += ["-pr", os.path.abspath(settings.profile)]

        for o in settings.options:
            cmd += ["-o", o]

        for s in settings.settings:
            cmd += ["-s", s]

        for c in settings.config:
            cmd += ["-c", c]

        if settings.generator:
            cmd += ["-g", settings.generator]

        if settings.output_folder:
            cmd += [f"--output-folder={os.path.abspath(settings.output_folder)}"]

        f = io.StringIO()
        conan_api = ConanAPI()
        conan_cli = ConanCli(conan_api)
        with redirect_stdout(f):
            conan_cli.run(cmd)
        out = f.getvalue()
        data = json.loads(out)
        return data["graph"]["nodes"]["0"]


def _build_wheel_impl(
    wheel_directory: str,
    config_settings: dict[str, list[str] | str] | None = None,
    metadata_directory: str | None = None,
    *,
    editable: bool,
) -> str:
    # Load settings for scikit-build
    skbuild_settings = SettingsReader.from_file("pyproject.toml").settings
    build_type = skbuild_settings.cmake.build_type

    # Load settings for scikit-build-core-conan
    prefixes = ["tool", "scikit-build-core-conan"]
    with Path("pyproject.toml").open("rb") as f:
        pyproject = tomllib.load(f)
        pyproject = copy.deepcopy(pyproject)

    process_overides(
        pyproject.get("tool", {}).get("scikit-build-core-conan", {}), "editable" if editable else "wheel", None
    )
    # noinspection PyTypeChecker
    conan_settings = SourceChain(
        TOMLSource(*prefixes, settings=pyproject),
        prefixes=prefixes,
    ).convert_target(ConanSettings)

    # Detect conan profile if one is not specified
    if not conan_settings.profile:
        detect_profile()

    # Export local dependencies
    for recipe in conan_settings.local_recipes:
        conan_export_local_recipes(recipe)

    # Use a tmp folder for the toolchain file
    with tempfile.TemporaryDirectory() as tmp:
        if conan_settings.output_folder is None:
            conan_settings.output_folder = tmp

        # Install the C++ dependencies
        result = conan_install(conan_settings, build_type)

        # Get the path to the toolchain file from install outputs
        generator_folder = result["generators_folder"]
        toolchain_file = os.path.abspath(f"{generator_folder}/conan_toolchain.cmake")

        # Extend the cmake.args
        config_settings = {} if config_settings is None else config_settings
        config_settings["cmake.args"] = ";".join(
            skbuild_settings.cmake.args
            + [
                f"-DCMAKE_POLICY_DEFAULT_CMP0091=NEW",
                f"-DCMAKE_TOOLCHAIN_FILE={toolchain_file}",
                f"-DCMAKE_BUILD_TYPE={build_type}",
            ]
        )

        # Profit
        if not editable:
            return scikit_build_core.build.build_wheel(wheel_directory, config_settings, metadata_directory)
        else:
            return scikit_build_core.build.build_editable(wheel_directory, config_settings, metadata_directory)


def build_wheel(
    wheel_directory: str,
    config_settings: dict[str, list[str] | str] | None = None,
    metadata_directory: str | None = None,
) -> str:
    return _build_wheel_impl(wheel_directory, config_settings, metadata_directory, editable=False)


def build_editable(
    wheel_directory: str,
    config_settings: dict[str, list[str] | str] | None = None,
    metadata_directory: str | None = None,
) -> str:
    return _build_wheel_impl(wheel_directory, config_settings, metadata_directory, editable=True)
