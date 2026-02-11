from pydantic import BaseModel
import yaml  # type: ignore


class Settings(BaseModel):
    database_path: str
    css_path: str


def read_settings_from_config(config_path: str) -> Settings:
    with open(config_path, "r") as file:
        try:
            yaml_content = yaml.safe_load(file)
            return Settings(
                database_path=yaml_content["database_path"],
                css_path=yaml_content["css_path"],
            )
        except yaml.YAMLError as e:
            print("Could not read config file")
            raise e
