from dataclasses import dataclass, field
from pathlib import Path

from yaml import safe_load

DATADIR = Path.home() / ".sidekick"


@dataclass
class Logging:
    mode: str = "w"
    level: str = "INFO"


@dataclass
class Model:
    base_url: str
    name: str
    api_key: str = ""


@dataclass
class Config:
    model: Model = None
    logging: Logging = field(default_factory=Logging)


def read_config() -> Config:
    data = safe_load(Path(DATADIR / "config.yaml").read_text())
    config = Config()

    if "model" in data:
        model_data = data["model"]
        model_config = Model(base_url=model_data["base_url"], name=model_data["name"])
        config.model = model_config

    return config


runtime = read_config()
