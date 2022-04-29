import pymel.core as pc
from cg3.publish.models import Reportable


class CollectGeoSets(Reportable):
    """Collect sets with postfix '_geo'."""

    label = "Sets postfixed '_geo'"

    def collect(self):
        geo_sets = pc.ls(sets=True, regex="*_geo")
        if not geo_sets:
            self.messages.append(
                "No set detected. Add all publishable geo to a set ending with _geo"
            )
            self.failed = True
        else:
            num_sets = len(geo_sets)
            self.messages.append(
                f"Collected {num_sets} geo set{'s' if num_sets > 1 else ''}."
            )
        return geo_sets
