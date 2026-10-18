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
    num_ctx: int = 4096
    temperature: float = 0.7


@dataclass
class Models:
    small: Model = None
    large: Model = None


@dataclass
class Web:
    url: str
    api_key: str


@dataclass
class Config:
    models: Models = None
    logging: Logging = field(default_factory=Logging)
    web: Web = None
    max_loops: int = 3


def read_model_config(data: dict) -> Model:
    model = Model(base_url=data["base_url"], name=data["name"])

    if "api_key" in data:
        model.api_key = data["api_key"]

    if "num_ctx" in data:
        model.num_ctx = data["num_ctx"]

    if "temperature" in data:
        model.temperature = data["temperature"]

    return model


def read_config() -> Config:
    data = safe_load(Path(DATADIR / "config.yaml").read_text())
    config = Config()

    if "models" in data:
        small_model = read_model_config(data["models"]["small"])
        large_model = read_model_config(data["models"]["large"])

        config.models = Models(small=small_model, large=large_model)

    if "web" in data:
        web_data = data["web"]
        config.web = Web(url=web_data["url"], api_key=web_data["api_key"])

    if "max_loops" in data:
        config.max_loops = data["max_loops"]

    return config


runtime = read_config()
