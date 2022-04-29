from typing import List

import pymel.core as pc
from cg3.publish.models import Reportable


class CheckForHistory(Reportable):
    """Check for history."""

    label = "No History"
    
    def check(self, items):
        """The check method."""
        for mesh in [m for m in items if m.type() in self.types]:
            shape = mesh.getShape()
            if shape is None:
                continue
            connections = shape.connections(s=True, d=False)
            if connections:
                self.failed = True
                self.messages.append(f"Object '{mesh}' has history.")

    def get_default_parameters(self):
        """Default parameters."""
        return {"types": ["transform"]}

    def set_parameters(self, types: List[str] = None):
        """Set parameters and maybe perform checks."""
        self.types = types
