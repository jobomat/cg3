import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, ClassVar, Dict
from time import time
from string import Template

from cg3.env.settings import Settings


@dataclass
class Scene:
    kind: str
    name: str
    extension: str
    dep: str
    user: str = field(default="unknown")
    timestamp: int = None
    _version: int = None

    @property
    def version(self):
        return str(self._version).zfill(4)

    @version.setter
    def version(self, value: int):
        self._version = value

    def get_version(self):
        return self._version

    def as_dict(self):
        return {
            "kind": self.kind,
            "name": self.name,
            "extension": self.extension,
            "dep": self.dep,
            "user": self.user,
            "timestamp": self.timestamp,
            "version": self.version
        }


class AssetMeta(type):
    def __init__(cls, *args, **kwargs):
        cls._settings = None
        cls._user_settings = None
        cls._release_name_template = None
        cls._release_path_template = None
        cls._version_name_template = None
        cls._version_path_template = None
        cls._release_history_name_template = None
        cls._release_history_path_template = None

    @property
    def settings(cls):
        return cls._settings

    @settings.setter
    def settings(cls, s):
        cls._settings = s
        path_list = cls._settings.templates.get("release").split("/")
        cls._release_name_template = Template(path_list.pop(-1))
        cls._release_path_template = Template("/".join(path_list))
        path_list = cls._settings.templates.get("version").split("/")
        cls._version_name_template = Template(path_list.pop(-1))
        cls._version_path_template = Template("/".join(path_list))
        path_list = cls._settings.templates.get("release_history").split("/")
        cls._release_history_name_template = Template(path_list.pop(-1))
        cls._release_history_path_template = Template("/".join(path_list))
    
    @property
    def user_settings(cls):
        return cls._user_settings

    @user_settings.setter
    def user_settings(cls, us):
        cls._user_settings = us


@dataclass
class Asset(metaclass=AssetMeta):
    kind: str
    name: str
    extension: str
    deps: Dict[str, Scene] = field(default_factory=dict)
    release_history: Dict[str, Scene] = field(default_factory=dict)

    def __post_init__(self):
        self.base_dir = Asset.user_settings.local_project_location

        if not self.deps:
            start_dep = Asset.settings.kinds.get(self.kind).get(
                "start_dep", Asset.settings.default_start_dep
            )
            self.deps[start_dep] = []

    def __lt__(self, other):
        return self.name < other.name

    def create_folders(self):
        for dep in self.get_deps():
            self.get_version(dep).parent.mkdir(parents=True, exist_ok=True)
            self.get_release_path(dep).mkdir(parents=True, exist_ok=True)
            self.get_release_history_path(dep).mkdir(parents=True, exist_ok=True)

    def new_version(self, dep: str, user="unknown"):
        if not dep in self.deps:
            self.deps[dep] = []
        try:
            version = self.deps[dep][-1].get_version()
        except IndexError:
            version = 0
        self.deps[dep].append(
            Scene(self.kind, self.name, self.extension, dep, user, int(time()), version + 1)
        )

    def add_version_scene(self, dep: str, user: str, version: str, timestamp: str=None):
        if not self.deps.get(dep, False):
            self.deps[dep] = []
        self.deps[dep].append(
            Scene(
                self.kind, self.name, self.extension,
                dep, user, timestamp, int(version)
            )
        )

    def get_max_version_scene(self, dep: str):
        try:
            return max(self.deps[dep], key=lambda s: s.version)
        except ValueError:
            return None

    def get_version_scene(self, dep: str, version: str):
        try:
            version = int(version)
            scenes = [s for s in self.deps[dep] if s.get_version() == version]
            return scenes[0]
        except IndexError:
            return None

    def get_version(self, dep:str, version: str="latest") -> Scene:
        if version == "latest":
            scene = self.get_max_version_scene(dep)
        else:
            scene = self.get_version_scene(dep, version)
        if scene is None:
            print(f"Version {version} not found for {self.kind} '{self.name}' in department '{dep}'.")
            return None
        path = self._version_path_template.substitute(scene.as_dict())
        name = self._version_name_template.substitute(scene.as_dict())
        return Path(self.base_dir) / path / name

    def get_release_path(self, dep: str) -> Path:
        return Path(self.base_dir) / self._release_path_template.substitute(
            kind=self.kind, name=self.name, dep=dep
        )

    def get_release_name(self, dep: str) -> str:
        return self._release_name_template.substitute(
            kind=self.kind, name=self.name, dep=dep, extension=self.extension
        )

    def get_release(self, dep: str) -> Path:
        return  self.get_release_path(dep) / self.get_release_name(dep)

    def get_release_history_path(self, dep: str) -> Path:
        return Path(self.base_dir) / self._release_history_path_template.substitute(
            kind=self.kind, name=self.name, dep=dep, extension=self.extension
        )

    def get_release_history(self, dep: str) -> List[Path]:
        pass

    def get_deps(self):
        return list(self.deps.keys())

    def list_versions(self, dep):
        return self.deps.get(dep, None)
