import pymel.core as pc
from cg3.publish.models import Reportable


class CheckFreezedTransforms(Reportable):
    """Check for freezed transforms."""

    label = "Freezed Transforms"
    
    def check(self, items):
        """Check for Freeze Transforms"""
        for transform in [t for t in items if t.type() == "transform"]:
            translates_are_zero = [x == 0.0 for x in transform.getTranslation()]
            if not all(translates_are_zero):
                self.messages.append(
                    f"Object '{transform}' has nonzero transformation values."
                )
                self.failed = True
            rotations_are_zero = [x == 0.0 for x in transform.getRotation()]
            if not all(rotations_are_zero):
                self.messages.append(
                    f"Object '{transform}' has nonzero rotation values."
                )
                self.failed = True
            scales_are_one = [x == 1.0 for x in transform.getScale()]
            if not all(scales_are_one):
                self.messages.append(
                    f"Object '{transform}' has scale values different from (1,1,1)."
                )
                passed = False
