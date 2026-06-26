import os

from typing import ClassVar, Literal
from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    CliSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

ENV_CONF_PATH = "EXIFTREE_CONFIG_FILE"
DEFAULT_CONF_PATH = "./config/config.yaml"


class Global(BaseModel):
    log_level: str = "info"
    dry_run: bool = False


class FileFilters(BaseModel):
    min_width: int = 0
    min_height: int = 0
    extensions: list[str]


class InputFolder(BaseModel):
    path: str
    max_depth: int


class OutputFolder(BaseModel):
    base_path_template: str
    unknown_path_template: str
    duplicates_path_template: str
    drop_duplicates: bool = False


class Config(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_prefix="EXIFTREE_",
        env_nested_delimiter="_",
        nested_model_default_partial_update=True,
    )

    global_settings: Global
    file_filters: FileFilters
    action: Literal["copy", "move"] = "copy"

    input_folders: list[InputFolder]
    output_folder: OutputFolder

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            CliSettingsSource(settings_cls, cli_parse_args=True),
            env_settings,
            YamlConfigSettingsSource(settings_cls, yaml_file=os.getenv(ENV_CONF_PATH, DEFAULT_CONF_PATH)),
            file_secret_settings,
        )
