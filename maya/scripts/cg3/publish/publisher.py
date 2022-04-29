"""Module providing the core publishing class."""
import importlib
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Callable

from cg3.publish.models import Reportable, Action


def print_reporter(reportable: Reportable):
    """Report by printing to console."""
    print(reportable.__doc__)
    print("\t", "Failed" if reportable.failed else "Passed")
    for message in reportable.messages:
        print("\t", message)


class Publisher:
    """The core publisher class.
    It loads and provides collectors, checkers, exporters, processors.
    These can be arranged in a playlist.
    The playlist can be run.
    The results can be passed to callback functions.
    """

    def __init__(self, reporter_callbacks: List[Callable]=None, module_folders: List[str]=None):
        self.items = []
        self.availible_modules: Dict[str, Reportable] = {}
        self.module_parameters: Dict[str, dict] = {}
        self.playlist: List[str] = []
        self.stopped = False

        self.reporter_callbacks = [print_reporter]
        if reporter_callbacks is not None:
            self.reporter_callbacks = reporter_callbacks

        cwd = str(Path(__file__).parent)
        self.module_folders = [f"{cwd}/modules"]

        if module_folders:
            self.module_folders.extend(module_folders)

        self.load_availible_modules()

    def load_availible_modules(self):
        """initiate module loading in given folders."""
        for folder in self.module_folders:
            if folder not in sys.path:
                sys.path.append(folder)
            self.load_modules_in_folder(folder)

    def load_modules_in_folder(self, folder):
        """load all detected modules in folder"""
        for pyfile in Path(folder).glob("*.py"):
            modname = pyfile.name[:-3]
            if self.follows_naming_convention(modname):
                try:
                    module = importlib.import_module(f"{modname}")
                    reporter = getattr(module, modname)()
                    self.availible_modules[modname] = reporter
                    self.module_parameters[modname] = reporter.get_default_parameters()
                except AttributeError:
                    print(f"Module '{modname}' not loaded.")

    def follows_naming_convention(self, name):
        """True if classname starts with specific words."""
        return any((name.startswith("Collect"), name.startswith("Check")))

    def call_reporters(self, reportable: Reportable):
        for reporter in self.reporter_callbacks:
            reporter(reportable)

    def list_modules(self, action:Action):
        return [m for n, m in self.availible_modules.items() if m.type == action]
        
    def publish(self):
        """The collect, check, export, process function."""
        self.stopped = False
        self.items = []
        for modname in self.playlist:
            if self.stopped:
                break
            module = self.availible_modules[modname]
            module.reset()
            module.set_parameters(**self.module_parameters[modname])
            self.items.extend(module.collect() or [])
            module.check(self.items)
            module.export(self.items)
            self.call_reporters(module)
            if module.failed and module.stop_on_failed:
                self.stopped = True


# from cg3.publish.publisher import Publisher

# p = Publisher()
# p.playlist.append("CollectGeoSets")
# p.playlist.append("CollectGeoSetsMembers")
# p.playlist.append("CheckPostfixes")
# p.playlist.append("CheckForHistory")
# p.playlist.append("CheckMultipleShapeNodes")
# p.playlist.append("CheckInitialShadingGroupApplied")
# p.playlist.append("CheckFreezedTransforms")
# p.playlist.append("CheckLaminaFaces")
# p.playlist.append("CheckNonmanifoldGeometry")
# p.playlist.append("CheckZeroLengthEdges")

# p.publish()

# print(p.items)
