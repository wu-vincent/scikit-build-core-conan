from __future__ import annotations

import copy
import io
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path


if sys.version_info < (3, 11):
    import tomli as tomllib
else:
    import tomllib

from conan.api.output import ConanOutput
from conan.api.conan_api import ConanAPI
from conan.cli.cli import Cli as ConanCli
from conan.tools.env.environment import environment_wrap_command
from conans.util.files import save
import scikit_build_core.build
from conans.util.runners import conan_run
from scikit_build_core_conan.build.settings import (
    ConanSettings,
    ConanLocalRecipesSettings,
)
from scikit_build_core.settings.skbuild_read_settings import (
    SettingsReader,
    process_overides,
)
from scikit_build_core.settings.sources import SourceChain, TOMLSource

__all__ = ["_build_wheel_impl"]


def _conan_export_local_recipes(settings: ConanLocalRecipesSettings) -> None:
    path = os.path.abspath(settings.path)
    cmd = ["export", f"{path}"]

    if settings.name:
        cmd += ["--name", settings.name]

    if settings.version:
        cmd += ["--version", settings.version]

    conan_api = ConanAPI()
    conan_cli = ConanCli(conan_api)
    conan_cli.run(cmd)


def _conan_install(settings: ConanSettings, build_type: str) -> dict:
    path = Path(settings.path).absolute()

    # Use a tmp folder for conanfile to avoid modifying the existing CMakeUserPresets.json
    with tempfile.TemporaryDirectory() as tmp:
        for file in ["conanfile.txt", "conanfile.py"]:
            if (path / file).exists():
                shutil.copy(path / file, tmp)
                break

        # mostly reimplement conan.cli.commands.install
        conan_api = ConanAPI()
        conan_api.install
        conanfile_path = conan_api.local.get_conanfile_path(tmp, os.getcwd, py=None)
        output_folder = (
            os.path.normpath(os.path.join(os.getcwd(), settings.output_folder))
            if settings.output_folder
            else None
        )

        remotes = conan_api.remotes.list()
        lockfile = conan_api.lockfile.get_lockfile(conanfile_path=tmp)
        profiles = [
            os.path.abspath(settings.profile) if settings.profile else "default"
        ]

        profile = conan_api.profiles.get_profile(
            profiles,
            [f"build_type={build_type}", *settings.settings],
            settings.options,
            settings.config,
        )
        deps_graph = conan_api.graph.load_graph_consumer(
            conanfile_path,
            name="",
            version="",
            user="",
            channel="",
            profile_host=profile,
            profile_build=profile,
            lockfile=lockfile,
            remotes=remotes,
            update=False,
        )
        conan_api.graph.analyze_binaries(
            deps_graph, [settings.build], remotes, lockfile=lockfile
        )
        conan_api.install.install_binaries(deps_graph, remotes)
        conan_api.install.install_consumer(
            deps_graph, settings.generator, tmp, output_folder
        )
        lockfile = conan_api.lockfile.update_lockfile(
            lockfile, deps_graph, False, False
        )
        conan_api.lockfile.save_lockfile(lockfile, None)

        return deps_graph.root


def _conan_detect_profile():
    conan_api = ConanAPI()
    profiles = conan_api.profiles.list()
    if "default" not in profiles:
        profile_pathname = conan_api.profiles.get_path(
            "default", os.getcwd(), exists=False
        )
        detected_profile = conan_api.profiles.detect()
        contents = detected_profile.dumps()
        save(profile_pathname, contents)


def _conan_activate_env(conanfile, env_folder, env="conanbuild"):
    stdout = io.StringIO()
    cmd = environment_wrap_command(
        conanfile,
        env,
        env_folder,
        cmd=f'"{sys.executable}" -c "import json,os;print(json.dumps(dict(os.environ)))"',
    )
    conan_run(cmd, stdout)
    for line in stdout.getvalue().splitlines():
        if line.startswith("{") and line.endswith("}"):
            env_vars = json.loads(line)
            os.environ.update(env_vars)
            return
        else:
            ConanOutput().info(line)

    raise ValueError(f"Unable to activate environment {env}")


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
        pyproject.get("tool", {}).get("scikit-build-core-conan", {}),
        state="editable" if editable else "wheel",
        retry=False,
        env=None,
    )
    # noinspection PyTypeChecker
    conan_settings = SourceChain(
        TOMLSource(*prefixes, settings=pyproject),
        prefixes=prefixes,
    ).convert_target(ConanSettings)

    # Detect conan profile
    _conan_detect_profile()

    # Export local dependencies
    for recipe in conan_settings.local_recipes:
        _conan_export_local_recipes(recipe)

    # Use a tmp folder for the toolchain file
    with tempfile.TemporaryDirectory() as tmp:
        if not conan_settings.output_folder:
            conan_settings.output_folder = tmp

        # Install the C++ dependencies
        result = _conan_install(conan_settings, build_type)

        # Get the path to the toolchain file from install outputs
        generator_folder = result.conanfile.generators_folder
        toolchain_file = os.path.abspath(f"{generator_folder}/conan_toolchain.cmake")

        # Activate build env
        _conan_activate_env(result.conanfile, generator_folder)

        # Extend the cmake.args
        config_settings = {} if config_settings is None else config_settings
        config_settings["cmake.args"] = ";".join(
            skbuild_settings.cmake.args
            + [
                "-DCMAKE_POLICY_DEFAULT_CMP0091=NEW",
                f"-DCMAKE_TOOLCHAIN_FILE={toolchain_file}",
                f"-DCMAKE_BUILD_TYPE={build_type}",
            ]
        )

        # Profit
        if not editable:
            return scikit_build_core.build.build_wheel(
                wheel_directory, config_settings, metadata_directory
            )
        else:
            return scikit_build_core.build.build_editable(
                wheel_directory, config_settings, metadata_directory
            )
