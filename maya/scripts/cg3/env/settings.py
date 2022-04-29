"""
Module providing Classes, Mixins and functions
for easy management of JSON-Setting files
for specific Classes.
"""
import json
import sys
from pathlib import Path
from typing import Any

import pymel.core as pc
from cg3.env.vars import getenv


class Settings:
    """
    Class for reading and writing settings-JSON files
    and accessing settings-keys by class-dot-notation.
    """

    def __init__(self, json_file: str = ""):
        self.set_json(json_file)
        self.read()

    def set_json(self, json_file: str):
        self._json_file = Path(json_file)

    def read(self):
        if self._json_file.is_file():
            temp = self._json_file
            self.__dict__ = json.loads(self._json_file.read_text())
            self._json_file = temp

    def save(self):
        self._json_file.write_text(
            json.dumps(
                {k: v for k, v in self.__dict__.items() if not k.startswith("_")},
                indent=4,
            )
        )

    def __str__(self):
        return str({k: v for k, v in self.__dict__.items() if not k.startswith("_")})

    def has(self, key: str) -> bool:
        return True if self.__dict__.get(key, False) else False

    def get(self, key: str, default: Any) -> Any:
        return self.__dict__.get(key, default)


def get_user_settings() -> Settings:
    MAYA_APP_DIR = getenv("MAYA_APP_DIR")
    MAYA_VERSION = pc.versions.shortName()
    USER_SETTINGS = f"{MAYA_APP_DIR}/{MAYA_VERSION}/scripts/cg3.json"
    return Settings(USER_SETTINGS)


def get_project_settings() -> Settings:
    user_settings = get_user_settings()
    return Settings(user_settings.project_settings)


class ClassUserSettings(Settings):
    """Class for managing settings for classes."""

    def __init__(self, class_name: str, file_name: str):
        class_json_name = f"{class_name}.json"

        CLASS_JSON = Path(file_name).parent / class_json_name

        MAYA_APP_DIR = getenv("MAYA_APP_DIR")
        MAYA_VERSION = pc.versions.shortName()
        USER_SETTINGS = (
            f"{MAYA_APP_DIR}/{MAYA_VERSION}/scripts/cg3settings/{class_json_name}"
        )

        if Path(USER_SETTINGS).is_file():
            super().__init__(USER_SETTINGS)
        else:
            super().__init__(CLASS_JSON)

        self.set_json(USER_SETTINGS)


class SettingsManagerMixin:
    """
    Mixin to provide easy management of settings where
    one (static) part of the settings comes from the class
    and another (dynamic) part comes from a user-json-file.

    When reading the settings, first the class settings are read,
    then the user settings are read and they will replace any existing
    settings with the same name.

    Usage:
    class MyClass(SettingsManagerMixin):
        def __init__(self):
            self.init_settings()
            settings.my_setting = 1920
    """

    def init_settings(self):
        """This method has to be called if the mixin is used."""
        self.settings = ClassUserSettings(
            self.__class__.__name__, sys.modules[self.__module__].__file__
        )
