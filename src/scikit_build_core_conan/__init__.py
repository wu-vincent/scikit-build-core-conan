import scikit_build_core.build
from scikit_build_core.build import build_sdist, get_requires_for_build_editable, get_requires_for_build_sdist, \
    get_requires_for_build_wheel, prepare_metadata_for_build_editable, prepare_metadata_for_build_wheel

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


def build_wheel(
        wheel_directory: str,
        config_settings: dict[str, list[str] | str] | None = None,
        metadata_directory: str | None = None,
) -> str:
    return scikit_build_core.build.build_wheel(wheel_directory, config_settings, metadata_directory)


def build_editable(
        wheel_directory: str,
        config_settings: dict[str, list[str] | str] | None = None,
        metadata_directory: str | None = None,
) -> str:
    return scikit_build_core.build.build_editable(wheel_directory, config_settings, metadata_directory)
