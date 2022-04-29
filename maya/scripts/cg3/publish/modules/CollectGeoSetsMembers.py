import pymel.core as pc
from cg3.publish.models import Reportable


class CollectGeoSetsMembers(Reportable):
    """Collect members of sets with '_geo' postfix."""

    label = "Members of '_geo' sets"

    def collect(self):
        geo_sets = pc.ls(sets=True, regex="*_geo")
        meshes = []
        for geo_set in geo_sets:
            meshes.extend(geo_set.members())
            if not meshes:
                self.messages.append(f"No members in set '{geo_set}'.")
        if not meshes:
            self.failed = True
        else:
            self.messages.append(f"Collected {len(meshes)} Objects.")
        return meshes
