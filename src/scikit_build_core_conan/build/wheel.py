from __future__ import annotations

import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from conan.errors import ConanException

if sys.version_info < (3, 11):
    import tomli as tomllib
else:
    import tomllib

import scikit_build_core.build
from conan.api.conan_api import ConanAPI
from conan.api.output import ConanOutput
from conan.cli.cli import Cli as ConanCli
from conan.cli.printers import print_profiles
from conan.tools.env.environment import environment_wrap_command
from scikit_build_core.settings.skbuild_read_settings import SettingsReader
from scikit_build_core.settings.sources import SourceChain, TOMLSource

from scikit_build_core_conan.build.settings import (
    ConanLocalRecipesSettings,
    ConanSettings,
)

try:
    from scikit_build_core.settings.skbuild_read_settings import process_overrides
except ImportError:
    # Fallback to the old version where the function was `process_overides`
    from scikit_build_core.settings.skbuild_read_settings import (
        process_overides as process_overrides,
    )

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


def _make_abs_path(path, cwd=None):
    """convert 'path' to absolute if necessary (could be already absolute)
    if not defined (empty, or None), will return 'default' one or 'cwd'
    """
    if path is None:
        return None
    if os.path.isabs(path):
        return path
    cwd = cwd or os.getcwd()
    abs_path = os.path.normpath(os.path.join(cwd, path))
    return abs_path


def _normalize_build_policy(build: list[str] | str) -> list[str]:
    """Normalize build policy to a list of strings."""
    if isinstance(build, str):
        return [build] if build else ["missing"]
    return build if build else ["missing"]


def _conan_install(settings: ConanSettings, build_type: str) -> dict:
    # mostly reimplement conan.cli.commands.install
    conan_api = ConanAPI()
    cwd = os.getcwd()
    path = conan_api.local.get_conanfile_path(settings.path, cwd, py=None)

    # Use a tmp folder for conanfile to avoid modifying the existing CMakeUserPresets.json
    with tempfile.TemporaryDirectory() as tmp:
        # copy the conanfile to the temporary dir
        shutil.copy(path, tmp)

        # basic paths
        path = conan_api.local.get_conanfile_path(tmp, cwd, py=None)
        source_folder = os.path.dirname(path)
        output_folder = _make_abs_path(settings.output_folder, cwd) if settings.output_folder else None

        # Basic collaborators: remotes, lockfile, profiles
        remotes = conan_api.remotes.list(settings.remote) if not settings.no_remote else []

        # Lockfile handling
        lockfile_path = _make_abs_path(settings.lockfile, cwd) if settings.lockfile else None
        lockfile = conan_api.lockfile.get_lockfile(
            lockfile=lockfile_path,
            conanfile_path=path,
            partial=settings.lockfile_partial,
        )

        build_profiles = [settings.profile_all or settings.profile_build or conan_api.profiles.get_default_build()]
        host_profiles = [settings.profile_all or settings.profile or conan_api.profiles.get_default_host()]
        build_settings = [s for settings in (settings.settings_build, settings.settings_all) for s in settings]
        host_settings = [s for settings in (settings.settings, settings.settings_all) for s in settings]
        profile_build = conan_api.profiles.get_profile(
            profiles=build_profiles,
            settings=[f"build_type={build_type}", *build_settings],
            options=[o for options in (settings.options_build, settings.options_all) for o in options],
            conf=[c for conf in (settings.config_build, settings.config_all) for c in conf],
            cwd=cwd,
            context="build",
        )
        profile_host = conan_api.profiles.get_profile(
            profiles=host_profiles,
            settings=[f"build_type={build_type}", *host_settings],
            options=[o for options in (settings.options, settings.options_all) for o in options],
            conf=[c for conf in (settings.config, settings.config_all) for c in conf],
            cwd=cwd,
            context="host",
        )
        print_profiles(profile_host=profile_host, profile_build=profile_build)

        # Graph computation (without installation of binaries)
        gapi = conan_api.graph
        deps_graph = gapi.load_graph_consumer(
            path,
            name=settings.name,
            version=settings.version,
            user=settings.user,
            channel=settings.channel,
            profile_host=profile_host,
            profile_build=profile_build,
            lockfile=lockfile,
            remotes=remotes,
            update=settings.update,
        )
        deps_graph.report_graph_error()

        # Normalize build policy (support both string and list)
        build_policy = _normalize_build_policy(settings.build)
        gapi.analyze_binaries(deps_graph, build_policy, remotes, update=settings.update, lockfile=lockfile)

        # Installation of binaries and consumer generators
        conan_api.install.install_binaries(deps_graph, remotes)
        ConanOutput().title("Finalizing install (deploy, generators)")
        deployer_folder = _make_abs_path(settings.deployer_folder, cwd) if settings.deployer_folder else output_folder
        conan_api.install.install_consumer(
            deps_graph,
            settings.generator,
            source_folder,
            output_folder,
            deploy=settings.deployer,
            deploy_package=settings.deployer_package,
            deploy_folder=deployer_folder,
        )

        ConanOutput().success("Install finished successfully")

        # Update lockfile if necessary
        lockfile = conan_api.lockfile.update_lockfile(
            lockfile,
            deps_graph,
            lock_packages=False,
            clean=settings.lockfile_clean,
        )
        conan_api.lockfile.save_lockfile(lockfile, settings.lockfile_out, None)
        return deps_graph.root


def _conan_detect_profile():
    conan_api = ConanAPI()
    profiles = conan_api.profiles.list()
    if "default" not in profiles:
        profile_pathname = conan_api.profiles.get_path("default", os.getcwd(), exists=False)
        detected_profile = conan_api.profiles.detect()
        dir_path = os.path.dirname(profile_pathname)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        contents = detected_profile.dumps()
        with open(profile_pathname, "w", encoding="utf-8", newline="") as f:
            f.write(contents)


def _conan_activate_env(conanfile, env_folder, env="conanbuild"):
    command = environment_wrap_command(
        conanfile,
        env,
        env_folder,
        cmd=f'"{sys.executable}" -c "import json,os;print(json.dumps(dict(os.environ)))"',
    )
    try:
        proc = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=None,
        )
    except Exception as e:
        raise ConanException(f"Error while running cmd\nError: {str(e)}")

    proc_stdout, proc_stderr = proc.communicate()
    if proc_stdout:
        for line in proc_stdout.decode("utf-8", errors="ignore").splitlines():
            if line.startswith("{") and line.endswith("}"):
                env_vars = json.loads(line)
                os.environ.update(env_vars)
                return
            else:
                ConanOutput().info(line)

    if proc_stderr:
        ConanOutput().error(proc_stderr.decode("utf-8", errors="ignore"))

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

    process_overrides(
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
            return scikit_build_core.build.build_wheel(wheel_directory, config_settings, metadata_directory)
        else:
            return scikit_build_core.build.build_editable(wheel_directory, config_settings, metadata_directory)
