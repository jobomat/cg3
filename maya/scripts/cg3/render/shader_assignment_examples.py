import cg3.render.shaders as s3

# call update every time the shaders changed (new shaders, shaders referenced...)
s3.update_staticUid_map()

# select objects or groups containing objects.
# to write the shader_assignments to the shape run:
for obj in pc.selected():
    shapes = obj.listRelatives(ad=True, type="shape")
    for shape in shapes:
        if shape and isinstance(shape, pc.nodetypes.Mesh):
            s3.write_shader_assignment(shape)
# in case of alembic-caching keep in mind to export the attribute "shaderAssignments"!


# to reassign shaders selecte objects or groups containing objects and run:
for obj in pc.selected():
    shapes = obj.listRelatives(ad=True, type="shape")
    for shape in shapes:
        s3.reassign_shaders(shape)


# collect shaderAssignments info. Interesting for potential GUI-Listings...
shapes_with_assignment = {}
shapes_without_assignment = {}
for obj in pc.selected():
    shapes = obj.listRelatives(ad=True, type="shape")
    for shape in shapes:
        if shape.hasAttr("shaderAssignments"):
            sgs = [sg.split(":") for sg in json.loads(
                shape.shaderAssignments.get()).keys()]

            shapes_with_assignment[shape.name()] = {
                "shadingGroups": sgs
            }

print(shapes_with_assignment)