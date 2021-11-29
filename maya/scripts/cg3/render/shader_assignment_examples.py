"""
Provide examples for usage of shaders module
"""
import json
import pymel.core as pc
from cg3.render.shaders import (
    write_shader_assignment, reassign_shaders
)
# call update every time the shaders changed (new shaders, shaders referenced...)
# deprecated shaders.update_staticUid_map()

# select objects or groups containing objects.
# to write the shader_assignments to the shape run:
sel = pc.selected()
for obj in sel:
    shapes = obj.listRelatives(ad=True, type="shape")
    for shape in shapes:
        if shape and isinstance(shape, pc.nodetypes.Mesh):
            write_shader_assignment(shape)
# in case of alembic-caching keep in mind to export the attribute "shaderAssignments"!


# to reassign shaders selecte objects or groups containing objects and run:
for obj in pc.selected():
    shapes = obj.listRelatives(ad=True, type="shape")
    for shape in shapes:
        reassign_shaders(shape)


# collect shaderAssignments info. Interesting for potential GUI-Listings...
shapes_with_assignment = {}

for obj in pc.selected():
    shapes = obj.listRelatives(ad=True, type="shape")
    for shape in shapes:
        if shape.hasAttr("shaderAssignments"):
            shapes_with_assignment[shape.name()] = json.loads(
                shape.shaderAssignments.get())

print(shapes_with_assignment)



shader_files = pc.fileDialog2(fileFilter="*.ma", fileMode=4)
suids_in_file = s3.list_suid_in_file(shader_files[0])
suids_in_scene = s3.list_suid_shaders()
for suid, shaders in suids_in_scene.items():
    if suid in suids_in_file:
        print(f"staticUid '{suid}' already present. Shaders: {[s.name() for s in shaders]}")
        pc.select(shaders, add=True, ne=True)
