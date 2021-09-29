import os
import platform
import json

import pymel.core as pc

from cg3.ui.windows import WinWrapper
from cg3.ui.widgets import file_chooser_button


FRAME_RATE_MAP = {
    "film": 24,
    "game": 15,
    "pal": 25,
    "ntsc": 30,
    "show": 48,
    "palf": 50,
    "ntscf": 60
}


def setenv(var_name, var_content, auto_delimiter=True):
    if auto_delimiter:
        var_content = f'"{var_content}"'
    pc.mel.eval(f'putenv {var_name} {var_content};')


def putenv(var_name, var_content):
    setenv(var_name, var_content)


def getenv(var_name):
    return pc.mel.eval('getenv {};'.format(var_name))


def set_env_vars(env_vars, placeholders={}):
    """
    Set Maya Environment Variables via dictionary "env_vars".
    Dictionary Keys:
        "name": The name of the Maya Environment Var.
        "recursive": bool, if True not the folder but all subfolders will be added
        "replace": bool, if True an existing env var value will be replaced
        "values: list, a list of values to add to the env var.
    placeholder:
        A dictionary with "VARNAME": "VARVALUE" pairs.
        The contents of var["values"] may contain python format string syntax
        (e.g. "one/{two}/three"). If the name in curly braces matches with a key
        in the placeholder dict ("VARNAME") it will be replaced by the value
        in the placeholder dict ("VARVALUE"). 
    Allways availible placeholders are:
        VERSION_SHORT: The short Maya Version (e.g. 2022)
        OS: The operating System (Linux: Linux, Mac: Darwin, Windows: Windows)
    """
    placeholders["VERSION_SHORT"] = pc.versions.shortName()
    placeholders["OS"] = platform.system()

    for var_info in env_vars:
        var_name = var_info["name"]
        replace = var_info["replace"]
        recursive = var_info["recursive"]
        values = [v.format(**placeholders) for v in var_info["values"]]
        current_value = getenv(var_name).split(";")
        if "" in current_value:
            current_value.remove("")
        current_value = ";".join(current_value)

        if recursive:
            folders = values[:]
            values = []
            for folder in folders:
                for root, *_ in os.walk(folder):
                    values.append(root.replace("\\", "/"))

        if "" in values:
            values.remove("")
        value = ";".join(values)

        if not replace and current_value:
            value = f"{current_value};{value}"

        print(f"\nSetting environment variable '{var_name}':")
        print("\n".join(value.split(";")))
        putenv(var_name, value)
                 

class EnvManager(WinWrapper):
    def __init__(self):
        super().__init__("envmanager_win", "Env Manager")

        self.ratios = (2, 6, 2, 2, 1)

        self.envs = []

        self.top = self.add_top_layout(pc.horizontalLayout)
        pc.button(
            parent=self.top, label="Add Environment Variable",
            c=pc.Callback(self.add_env)
        )

        self.mid = self.add_mid_layout(pc.columnLayout, adj=True)

        self.bottom = self.add_bottom_layout(pc.horizontalLayout)
        pc.button(parent=self.bottom, label="Load JSON", c=self.load_json)
        pc.button(parent=self.bottom, label="Save JSON", c=self.save_json)
        pc.button(parent=self.bottom, label="Close")
        self.bottom.redistribute()

    def add_env(self, data=None):
        data = {} if data is None else data
        env = {}
        with pc.columnLayout(adj=True, parent=self.mid) as env["row"]:
            with pc.horizontalLayout(ratios=self.ratios):
                pc.text(label="Variable Name")
                env["name"] = pc.textField(text=data.get("name",""))
                env["replace"] = pc.checkBox(
                    label="Replace", value=data.get("replace", False)
                )
                env["recursive"] = pc.checkBox(
                    label="Recursive", value=data.get("recursive", False)
                )
                env["delete"] = pc.iconTextButton(
                    style="iconOnly", i="delete.png",
                    c=pc.Callback(self.delete_env, env)
                )
                env["values"] = []
            with pc.horizontalLayout(ratios=(1, 1, 11)):
                pc.text(label="Values")
                pc.iconTextButton(
                    style="iconOnly", i="addClip.png",
                    c=pc.Callback(self.add_value, env)
                )
                with pc.columnLayout(adj=True) as env["value_cl"]:
                    pass
        
        self.envs.append(env)
        for val in data.get("values", []):
            self.add_value(env, val)

    def delete_env(self, env):
        pc.deleteUI(env["row"])
        self.envs.remove(env)

    def add_value(self, env, value=None):
        with pc.rowLayout(nc=2, parent=env["value_cl"], adj=1) as rl:
            file_chooser_button(
                "Value", 2, "Add Dir/File", text="" if value is None else value,
                tfb_kwargs={"cw":(1, 40)},
                okCaption="Choose Dir/File"
            )
            pc.iconTextButton(
                style="iconOnly", i="delete.png",
                c=pc.Callback(self.delete_value, env, rl)
            )
        env["values"].append(rl)

    def delete_value(self, env, rl):
        pc.deleteUI(rl)
        env["values"].remove(rl)

    def load_json(self, *args):
        json_file = pc.fileDialog2(
            dialogStyle=2, fileMode=1, fileFilter="JSON (*.json)"
        )
        if not json_file:
            return
        
        with open(json_file[0]) as jf:
            data = json.load(jf)
        self.envs = []
        for child in self.mid.getChildren():
            pc.deleteUI(child)

        for env in data:
            self.add_env(env) 

    def save_json(self, *args):
        env_vars = []
        for env in self.envs:
            value_tfs = [c.getChildren()[0].getChildren()[1] for c in env["values"]]
            name = env["name"].getText()
            replace = env["replace"].getValue()
            recursive = env["recursive"].getValue()
            values = [tf.getText() for tf in value_tfs]
            if name and values:
                env_vars.append({
                    "name": name,
                    "replace": replace,
                    "recursive": recursive,
                    "values": values
                })
            else:
                pc.confirmDialog(
                    title='Validation Errors',
                    message='Please specify all Varable names and Values.'
                )
                return
        json_file = pc.fileDialog2(
            dialogStyle=2, fileMode=0
        )
        if not json_file:
            return
        
        with open(json_file[0], "w") as jf:
            json.dump(env_vars, jf, indent=4)
