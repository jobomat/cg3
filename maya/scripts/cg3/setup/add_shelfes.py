import os

from cg3.ui import shelfes
from cg3.env.vars import getenv


def build_shelfes():
    json_shelf_dir = os.path.normpath(
        os.path.join(getenv("CG3_MAYA_DIR"),"shelfes","json")
    )
    r, d, files = next(os.walk(json_shelf_dir))

    tls = shelfes.TopLevelShelf()
    for f in files:
        if f.endswith(".json"):
            tls.load_from_json(os.path.join(json_shelf_dir, f))


build_shelfes()
