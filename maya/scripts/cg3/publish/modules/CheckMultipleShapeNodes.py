import pymel.core as pc
from cg3.publish.models import Reportable


class CheckMultipleShapeNodes(Reportable):
    """Checks for multiple shape nodes in an object."""

    label = "One shape node only"

    def check(self, items):
        """Check for mulitple Shape Nodes"""
        for mesh in [m for m in items if hasattr(m, "getShapes")]:
            if len(mesh.getShapes()) > 1:
                self.failed = True
                self.messages.append(f"Multiple shapes detected in {mesh.name()}.")
