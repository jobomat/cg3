from pathlib import Path
from datetime import date, timedelta
import json

from cg3.file.dirtree import Dirtree

def project_dirtree(name:str, template:str,
                    start_weekly:tuple, end_weekly:tuple,
                    exclude_dates:list=None):
    exclude_weeklies = [
        (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6),
        (5, 1),
        (10, 3),
        (11, 1),
        (12, 24), (12, 25), (12, 26), (12, 27), (12, 28), (12, 29), (12, 30), (12, 31)
    ]
    if exclude_dates is not None:
        exclude_weeklies.extend(exclude_dates)

    dir_tree_path = Path(template)
    with dir_tree_path.open("r") as f:
        dir_tree_dict = json.load(f)
    dir_tree = Dirtree().from_dict(dir_tree_dict)
    dir_tree.name = name

    current_weekly = date(*start_weekly)
    end_weekly = date(*end_weekly)
    print(exclude_weeklies)

    while current_weekly <= end_weekly:
        if current_weekly.timetuple()[1:3] not in exclude_weeklies:
            dir_tree.weekly.add_new_dir(current_weekly.strftime("%Y_%m_%d"))
        current_weekly = current_weekly + timedelta(weeks=1)

    return dir_tree


# future use

# from pathlib import Path
# from cg3.minipipe.creators import project_dirtree
# d = project_dirtree(
#     "gruppe3",
#     "C:/Users/jobo/Documents/GoogleDrive/coding/python/cg3/maya/scripts/cg3/minipipe/templates/project_dirtree.json",
#     (2021, 10, 6), (2022, 1, 19)
# )

# d.get_dir("3d").get_file("workspace.mel").template = "workspace.mel"
# d.create(
#     Path("N:"),
#     Path("C:/Users/jobo/Documents/GoogleDrive/coding/python/cg3/maya/scripts/cg3/minipipe/templates/")
# )
