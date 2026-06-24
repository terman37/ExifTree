import os

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


class InputFolder(BaseModel):
    path: str
    max_depth: int


class OutputFolder(BaseModel):
    base_path: str
    template: str


class Config(BaseSettings):
    model_config: SettingsConfigDict = SettingsConfigDict(
        env_prefix="EXIFTREE_",
        env_nested_delimiter="_",
        nested_model_default_partial_update=True,
    )

    log_level: str = "info"
    dry_run: bool = False

    inputFolders: list[InputFolder]
    outputFolder: OutputFolder
    extensions: list[str]

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
