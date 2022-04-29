from typing import List

import pymel.core as pc
from cg3.publish.models import Reportable


class CheckPostfixes(Reportable):
    """Check user specified Postfixes."""

    label = "Specific Postfixes"

    def set_parameters(self, postfixes: List[str] = None):
        if postfixes is None:
            postfixes = ["_geo"]
        self.postfixes = postfixes

    def check(self, items):
        """Checks collected items for certain postfixes.
        Default it checks for '_geo'.
        This checker doesn't check if the postfix matches with object-type."""
        for item in items:
            if not any([item.name().endswith(p) for p in self.postfixes]):
                self.messages.append(
                    f"Missing postfix on '{item.name()}'. Expected: {self.postfixes}"
                )
                self.failed = True
