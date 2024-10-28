import os

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvSettings(BaseSettings):
    # this is to take in all the environment variables
    # this is for the logging purpose
    # when deployed on cloud, the name and ver should come from envvar
    ENV: str
    SERVICE_NAME: str
    SERVICE_VERSION: str
    NAMESPACE: str

    LLM_API_KEY: str
    LLM_GATEWAY: str
    LLM_MODEL: str


class LocalDevSettings(EnvSettings):
    # it reads from a config file at root
    # this config file is gitignored
    # this config file needs to have a template
    model_config = SettingsConfigDict(env_file="config", extra="ignore")


class DeployedSettings(EnvSettings):
    # takes in env vars from the pod
    ...


def find_config() -> EnvSettings:
    if os.getenv("ENV"):
        return DeployedSettings()
    else:
        return LocalDevSettings()


env = find_config()


if __name__ == "__main__":
    print(env)
