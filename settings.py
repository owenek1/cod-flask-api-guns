import toml
from dotenv import load_dotenv

class Settings():
  
  def __init__(self):
        load_dotenv(verbose=True)
        self.py_project = toml.load("pyproject.toml")

  # Generic App and Flask settings
  @property
  def app_name(self) -> str:
      return self.py_project["tool"]["poetry"]["name"]

  @property
  def app_version(self) -> str:
      return self.py_project["tool"]["poetry"]["version"]
  
  @property
  def app_description(self) -> str:
      return self.py_project["tool"]["poetry"]["description"]
  
  # @property
  # def app_port(self) -> int:
  #     return self._get_env("APP_PORT", int, 80)
  
  # @property
  # def app_env(self) -> str:
  #     return self._get_env("FLASK_ENV", str, "development")
