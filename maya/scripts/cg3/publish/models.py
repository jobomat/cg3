from dataclasses import dataclass, field
from typing import Any, List
from enum import Enum


class Action(Enum):
  Collect = 0
  Check = 1
  Export = 2

  def __str__(self):
    return self.name


@dataclass
class Reportable:
    failed: bool = False
    stop_on_failed: bool = True
    messages: list = field(default_factory=list)

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @property
    def type(self) -> Action:
        for name, action in Action.__members__.items():
            if self.name.startswith(name):
                return action

    def get_default_parameters(self) -> dict:
        return {}

    def set_parameters(self, **kwargs):
        pass

    def reset(self):
        self.failed = False
        self.messages = []

    def collect(self, *args, **kwargs) -> List[Any]:
        return []

    def check(self, items):
        pass

    def export(self, items):
        pass
