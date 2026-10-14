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
class Web:
    url: str
    api_key: str


@dataclass
class Config:
    model: Model = None
    logging: Logging = field(default_factory=Logging)
    web: Web = None


def read_config() -> Config:
    data = safe_load(Path(DATADIR / "config.yaml").read_text())
    config = Config()

    if "model" in data:
        model_data = data["model"]
        model_config = Model(base_url=model_data["base_url"], name=model_data["name"])

        if "api_key" in model_data:
            model_config.api_key = model_data["api_key"]

        if "num_ctx" in model_data:
            model_config.api_key = model_data["num_ctx"]

        if "temperature" in model_data:
            model_config.api_key = model_data["temperature"]

        config.model = model_config

    if "web" in data:
        web_data = data["web"]
        config.web = Web(url=web_data["url"], api_key=web_data["api_key"])

    return config


runtime = read_config()
