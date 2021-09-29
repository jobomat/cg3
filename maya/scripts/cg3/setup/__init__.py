import inspect
import os
import json

from maya.utils import executeDeferred

from cg3.env.vars import set_env_vars


executeDeferred("import cg3.setup.add_venvs")
executeDeferred("import cg3.setup.add_toolbox_buttons")
executeDeferred("import cg3.setup.add_shelfes")

this_file_path = inspect.getfile(lambda: None).replace("\\", "/")

CG3_MAYA_DIR = "/".join(this_file_path.split("/")[:-4])
SETUP_DIR = "/".join(this_file_path.split("/")[:-1])

with open(os.path.join(SETUP_DIR, "maya_envs.json")) as jf:
    envvars = json.load(jf)

set_env_vars(envvars, {"base": CG3_MAYA_DIR})
