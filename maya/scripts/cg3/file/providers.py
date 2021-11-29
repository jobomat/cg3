from oauth2client.service_account import ServiceAccountCredentials
import gspread
from abc import ABC, abstractmethod
from typing import List
from pathlib import Path
import re

from cg3.file.models import Asset
from cg3.env.settings import get_project_settings, get_user_settings
from cg3.event import cg3event


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

    @abstractmethod
    def on_asset_created(self, asset:Asset):
        """Do whatever is necessary if new Asset is created"""


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
        self.assets = {name: Asset(kind, name, "ma") for kind, name in kind_name}
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

    def on_asset_created(self, asset):
        print(asset)


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


class GoogleSheetsAssetProvider(AssetProvider):
    def __init__(self, auth_json: str, sheet_name: str, settings=None):
        Asset.settings = self.settings = settings or get_project_settings()
        Asset.user_settings = self.user_settings = get_user_settings()

        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(auth_json, scope)
        client = gspread.authorize(creds)

        self.asset_sheet = client.open(sheet_name).sheet1

        self.assets = {}
        self.reload_asset_list()

    def sort_asset_sheet(self):
        # sort by asset, kind, dep, version
        # so the reload_asset_list method will work correct
        self.asset_sheet.sort(
            (1, "asc"), (2, "asc"), (4, "asc"), (5, "asc")
        )

    def reload_asset_list(self):
        self.sort_asset_sheet()
        results = self.asset_sheet.get_all_records()

        current_asset_name = None
        #current_dep = None

        for result in results:
            asset_name = result["asset"]
            if current_asset_name != asset_name:
                current_asset_name = result["asset"]
                self.assets[current_asset_name] = Asset(
                    result["kind"], current_asset_name, result["extension"]
                )
                #current_dep = None
            else:
                dep = result["dep"]
                user = result["user"]
                version = str(result["version"]).zfill(4)
                timestamp = str(result["timestamp"])
                comment = result["comment"]
                self.assets[current_asset_name].add_version_scene(
                    dep, user, version, timestamp, comment
                )
    
    def get(self, name: str) -> Asset:
        return self.assets.get(name, None)

    def list_assets(self) -> List[Asset]:
        return sorted(self.assets.values())

    def on_asset_created(self, asset):
        """On creation add two rows.
        Fist one for the asset "idea", 
        the second for the first created file."""
        self.assets[asset.name] = asset
        start_dep = asset.get_start_dep()
        scene = asset.get_max_version_scene(start_dep)
        self.asset_sheet.append_row((
            asset.name, asset.kind, "WIP",
            None, None,None, None, None, scene.extension
        ))
        self.asset_sheet.append_row((
            asset.name, None, None,
            start_dep, 1, "Initial Save",
            scene.user, scene.timestamp, scene.extension
        ))
        self.reload_asset_list()
        

