import pymel.core as pc
from cg3.publish.models import Reportable


class CheckInitialShadingGroupApplied(Reportable):
    """Check that only 'initialShadingGroup' is applied."""

    label = "Initial Shading Group"

    def check(self, items):
        """Check for shadingEngines with name other than 'initialShadingGroup'."""
        for mesh in [m for m in items if hasattr(m, "getShapes")]:
            connections = mesh.getShape().connections(type="shadingEngine")
            if connections[0].name() != "initialShadingGroup":
                self.messages.append(f"Object '{mesh}' has shaders assigned.")
                self.failed = True
