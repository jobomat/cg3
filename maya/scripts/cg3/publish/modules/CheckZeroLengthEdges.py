import pymel.core as pc
from cg3.publish.models import Reportable


class CheckZeroLengthEdges(Reportable):
    """Check for edges with zero length."""

    label = "No Zero Length Edges"

    def check(self, items):
        """Select all items and run cleanup with 'Edges with zero length' checked."""
        pc.select(items, r=True)
        pc.mel.eval(
            'polyCleanupArgList 4 { "0","2","1","0","0","0","0","0","0","1e-05","1","1e-05","0","1e-05","0","-1","0","0" };'
        )
        sel = pc.selected()
        if sel:
            self.failed = True
            self.messages.append(f"Edges with zero length deteced:\n\t\t{sel}.")
