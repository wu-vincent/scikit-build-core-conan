import io
import json
import os
import shutil
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

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
from scikit_build_core.settings.skbuild_read_settings import SettingsReader

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


def conan_install(path: str, build_type: str, output_folder: str) -> dict:
    path = Path(path).absolute()
    output_folder = Path(output_folder).absolute()

    # Use a tmp folder for conanfile to avoid modifying the existing CMakeUserPresets.json
    with tempfile.TemporaryDirectory() as tmp:
        for file in ["conanfile.txt", "conanfile.py"]:
            if (path / file).exists():
                shutil.copy(path / file, tmp)
                break

        cmd = [
            "install",
            f"{tmp}",
            "--build=missing",
            "-s",
            f"build_type={build_type}",
            f"--output-folder={output_folder}",
            "--format=json",
        ]
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
    settings = SettingsReader.from_file("pyproject.toml").settings
    build_type = settings.cmake.build_type

    # Use a tmp folder for the toolchain file
    with tempfile.TemporaryDirectory() as tmp:
        # Install the C++ dependencies
        result = conan_install(".", build_type, tmp)

        # Get the path to the toolchain file from install outputs
        generator_folder = result["generators_folder"]
        toolchain_file = os.path.abspath(f"{generator_folder}/conan_toolchain.cmake")

        # Extend the cmake.args
        config_settings = {} if config_settings is None else config_settings
        config_settings["cmake.args"] = ";".join(
            settings.cmake.args
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
