from pathlib import Path
import json
import importlib

from cg3.env.vars import getenv
from cg3.env.settings import SettingsManagerMixin
from cg3.event import cg3event


class Plugins(SettingsManagerMixin):
    def __init__(self):
        self.init_settings()
        self.plugins = {}
        self.plugin_module_path = Path(getenv("CG3_MAYA_DIR")) / "scripts/cg3/plugin/"
        self.load_default_plugins()

    def load_default_plugins(self):
        plugin_json = self.plugin_module_path / "default_plugins.json"
        with plugin_json.open("r") as pj:
            plugin_config = json.load(pj)
        
        self.load_plugins(plugin_config)

    def load_plugins(self, config):
        plugin_loader_path = self.plugin_module_path / "plugins"
        for modname, conf in config.items():
            module = importlib.import_module(f"cg3.plugin.plugins.{modname}.{modname}")
            plug_class = getattr(module, "initialize")()
            self.plugins[modname] = plug_class
            for event, fn_str in conf["listen_to"].items():
                cg3event.subscribe(event, getattr(plug_class(), fn_str))
