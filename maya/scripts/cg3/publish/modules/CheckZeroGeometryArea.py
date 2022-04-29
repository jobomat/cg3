import pymel.core as pc
from cg3.publish.models import Reportable


class CheckZeroGeometryArea(Reportable):
    """Check for faces with zero area."""

    label = "No Zero Area Faces"

    def check(self, items):
        """Select all items and run cleanup with 'Faces with zero geometry area' checked."""
        pc.select(items, r=True)
        pc.mel.eval(
            'polyCleanupArgList 4 { "0","2","1","0","0","0","0","0","1","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };'
        )
        sel = pc.selected()
        if sel:
            self.failed = True
            self.messages.append(f"Faces with zero area deteced:\n\t\t{sel}.")
