import logging
from pathlib import Path
from typing import Literal

from langchain_ollama import ChatOllama
from pydantic import BaseModel, ConfigDict, HttpUrl
from yaml import safe_load

DATADIR = Path.home() / ".sidekick"


class Logging(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    mode: Literal["a", "w"] = "w"
    level: Literal["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "FATAL"] = "INFO"


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    base_url: HttpUrl
    name: str


class Models(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    small: Model
    large: Model


class ModelInfo(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    model: Literal["small", "large"]
    num_ctx: int = 4096
    temperature: float = 0.7


type Role = Literal["plan", "research", "answer", "factcheck", "critic"]


class Roles(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    plan: ModelInfo = None
    research: ModelInfo = None
    answer: ModelInfo = None
    factcheck: ModelInfo = None
    critic: ModelInfo = None


class Web(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    url: HttpUrl
    api_key: str


class Config(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    models: Models
    roles: Roles
    logging: Logging = Logging()
    web: Web
    max_loops: int = 3


runtime = Config.model_validate(safe_load(Path(DATADIR / "config.yaml").read_text()))
logging.basicConfig(
    filename=DATADIR / "app.log",
    filemode=runtime.logging.mode,
    level=runtime.logging.level,
)


def get_model(role: Role):
    model_params: ModelInfo = runtime.roles.__getattribute__(role)

    model_size = (
        runtime.models.small
        if model_params and model_params.model == "small"
        else runtime.models.large
    )

    return ChatOllama(
        model=model_size.name,
        base_url=str(model_size.base_url),
        num_ctx=model_params.num_ctx if model_params else None,
        temperature=model_params.temperature if model_params else None,
    )
