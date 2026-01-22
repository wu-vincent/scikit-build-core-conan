from dataclasses import dataclass, field


@dataclass
class ConanLocalRecipesSettings:
    path: str = "."
    name: str = ""
    version: str = ""


@dataclass
class ConanSettings:
    path: str = "."
    # options
    build: list[str] | str = "missing"
    generator: str = ""
    output_folder: str = ""
    deployer: list[str] = field(default_factory=list)
    deployer_folder: str = ""
    deployer_package: list[str] = field(default_factory=list)
    # remote arguments
    remote: list[str] = field(default_factory=list)
    no_remote: bool = False
    update: bool = False
    # profile arguments
    profile: str = ""
    profile_build: str = ""
    profile_all: str = ""
    options: list[str] = field(default_factory=list)
    options_build: list[str] = field(default_factory=list)
    options_all: list[str] = field(default_factory=list)
    settings: list[str] = field(default_factory=list)
    settings_build: list[str] = field(default_factory=list)
    settings_all: list[str] = field(default_factory=list)
    config: list[str] = field(default_factory=list)
    config_build: list[str] = field(default_factory=list)
    config_all: list[str] = field(default_factory=list)
    # reference arguments
    name: str = ""
    version: str = ""
    user: str = ""
    channel: str = ""
    # lockfile arguments
    lockfile: str = ""
    lockfile_partial: bool = False
    lockfile_out: str = ""
    lockfile_clean: bool = False
    # custom extensions
    local_recipes: list[ConanLocalRecipesSettings] = field(default_factory=list)
