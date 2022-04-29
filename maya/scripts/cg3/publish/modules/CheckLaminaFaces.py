import pymel.core as pc
from cg3.publish.models import Reportable


class CheckLaminaFaces(Reportable):
    """Check for lamina faces."""

    label = "No Lamina Faces"

    def check(self, items):
        """Select all items and run cleanup with only lamina faces checked."""
        pc.select(items, r=True)
        pc.mel.eval(
            'polyCleanupArgList 4 { "0","2","1","0","0","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","-1","1","0" };'
        )
        sel = pc.selected()
        if sel:
            self.failed = True
            self.messages.append(f"Lamina Faces deteced.\n\t\t{sel}.")
