import dataclasses


@dataclasses.dataclass
class ConanLocalRecipesSettings:
    path: str = "."
    name: str = ""
    version: str = ""


@dataclasses.dataclass
class ConanSettings:
    # common
    path: str = "."
    # common install
    build: str = "missing"
    remote: list[str] | None = None
    no_remote: bool = False
    # profile
    profile: str = ""
    profile_build: str = ""
    profile_all: str = ""
    options: list[str] = dataclasses.field(default_factory=list)
    options_build: list[str] = dataclasses.field(default_factory=list)
    options_all: list[str] = dataclasses.field(default_factory=list)
    settings: list[str] = dataclasses.field(default_factory=list)
    settings_build: list[str] = dataclasses.field(default_factory=list)
    settings_all: list[str] = dataclasses.field(default_factory=list)
    config: list[str] = dataclasses.field(default_factory=list)
    config_build: list[str] = dataclasses.field(default_factory=list)
    config_all: list[str] = dataclasses.field(default_factory=list)
    # install
    generator: str = ""
    output_folder: str = ""
    # extra
    local_recipes: list[ConanLocalRecipesSettings] = dataclasses.field(default_factory=list)
