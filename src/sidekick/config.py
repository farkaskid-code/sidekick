from pathlib import Path

from pydantic import BaseModel, ConfigDict
from yaml import safe_load

DATADIR = Path.home() / ".sidekick"


class Logging(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    mode: str = "w"
    level: str = "INFO"


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    base_url: str
    name: str
    api_key: str = ""
    num_ctx: int = 4096
    temperature: float = 0.7


class Models(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    small: Model = None
    large: Model = None


class Web(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    url: str
    api_key: str


class Config(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    models: Models = None
    logging: Logging = Logging()
    web: Web = None
    max_loops: int = 3


runtime = Config.model_validate(safe_load(Path(DATADIR / "config.yaml").read_text()))
