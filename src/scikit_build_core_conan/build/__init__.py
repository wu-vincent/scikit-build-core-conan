from __future__ import annotations

from scikit_build_core.build import (
    build_sdist,
    get_requires_for_build_editable,
    get_requires_for_build_sdist,
    get_requires_for_build_wheel,
    prepare_metadata_for_build_editable,
    prepare_metadata_for_build_wheel,
)

from scikit_build_core_conan.build.wheel import _build_wheel_impl

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
    return _build_wheel_impl(
        wheel_directory, config_settings, metadata_directory, editable=False
    )


def build_editable(
    wheel_directory: str,
    config_settings: dict[str, list[str] | str] | None = None,
    metadata_directory: str | None = None,
) -> str:
    return _build_wheel_impl(
        wheel_directory, config_settings, metadata_directory, editable=True
    )
