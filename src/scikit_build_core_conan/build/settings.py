import dataclasses
from typing import List


@dataclasses.dataclass
class ConanLocalRecipesSettings:
    path: str = "."
    name: str = ""
    version: str = ""


@dataclasses.dataclass
class ConanSettings:
    path: str = "."
    build: str = "missing"
    profile: str = ""
    options: List[str] = dataclasses.field(default_factory=list)
    settings: List[str] = dataclasses.field(default_factory=list)
    config: List[str] = dataclasses.field(default_factory=list)
    generator: str = ""
    output_folder: str = ""
    local_recipes: List[ConanLocalRecipesSettings] = dataclasses.field(
        default_factory=list
    )
