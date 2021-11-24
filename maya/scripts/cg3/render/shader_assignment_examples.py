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
for obj in pc.selected():
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
