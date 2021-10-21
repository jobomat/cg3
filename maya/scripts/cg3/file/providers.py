from abc import ABC, abstractmethod
from typing import List
from pathlib import Path
import re

from cg3.file.models import Asset
from cg3.env.settings import get_project_settings, get_user_settings


class AssetProvider(ABC):
    settings = None
    @abstractmethod
    def get(self, name:str) -> Asset:
        """Returns  Asset by name"""

    @abstractmethod
    def list_assets(self) -> List[Asset]:
        """Returns a list of all Assets"""

    @abstractmethod
    def reload_asset_list(self):
        """Trigger a complete reload of the asset list."""


class MockAssetProvider(AssetProvider):
    def __init__(self, settings=None):
        Asset.settings = self.settings = settings or get_project_settings()
        Asset.user_settings = self.user_settings = get_user_settings()
        kind_name = (
            ("char", "bob"), ("char", "lisa"),
            ("prop", "chair"), ("prop", "table"), ("prop", "fork"),
            ("set", "kitchen"), ("set", "park"),
            ("seq", "s0100"), ("seq", "s0200"), ("seq", "s0250")
        )
        self.assets = {name: Asset(kind, name) for kind, name in kind_name}
        for _, asset in self.assets.items():
            asset.new_version(asset.get_deps()[0])
            if "e" in asset.name:
                asset.new_version(asset.get_deps()[0])
            elif asset.kind not in ["set", "seq"]:
                asset.new_version("shade")
            if asset.kind == "char":
                asset.new_version("rig")

    def get(self, name:str):
        return self.assets.get(name, None)

    def list_assets(self) -> List[Asset]:
        return self.assets.values()
    
    def reload_asset_list(self):
        pass


class FilesystemAssetProvider(AssetProvider):
    def __init__(self, settings=None):
        Asset.settings = self.settings = settings or get_project_settings()
        Asset.user_settings = self.user_settings = get_user_settings()

        self.assets = {}
        self.reload_asset_list()

    def on_asset_created(self, asset):
        self.assets[asset.name] = asset

    def reload_asset_list(self):
        match_string = Asset.user_settings.local_project_location
        match_string += "/" + Asset.settings.templates["version"]
        match_string = match_string.replace(".", "\.")
        first, *rest = match_string.split("${")

        # create a regex matchstring out of the template string
        var_name_seen = []
        match_list = [first]
        for part in rest:
            var_name, x = part.split("}")
            # search for a variable only once
            if var_name not in var_name_seen:
                match_list.append(f"(?P<{var_name}>.*){x}")
                var_name_seen.append(var_name)
            else:
                match_list.append(f".*{x}" if match_list[-1] != ".*" else x)
                
        match_string = "".join(match_list)
        regex = re.compile(match_string)

        # go throug all scene files with matching extension and match against match_string
        for full_path in Path(Asset.user_settings.local_project_location).rglob(f"*.*"):
            match = regex.match(str(full_path).replace("\\","/"))
            if match:
                groupdict = match.groupdict()
                asset = self.assets.get(groupdict["name"], None)
                if asset is None:
                    self.assets[groupdict["name"]] = Asset(
                        groupdict["kind"], groupdict["name"], groupdict["extension"]
                    )
                self.assets[groupdict["name"]].add_version_scene(
                    groupdict["dep"], groupdict["user"], 
                    groupdict["version"], groupdict.get("timestamp", None)
                )

    def get(self, name:str) -> Asset:
        return self.assets.get(name, None)

    def list_assets(self) -> List[Asset]:
        return sorted(self.assets.values())
