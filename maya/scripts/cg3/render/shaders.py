from uuid import uuid4
import json
import pymel.core as pc


suid_map = {}


def get_staticUid_map(force_update=False):
    global suid_map
    if suid_map and not force_update:
        return suid_map
    print("generating suid_map")
    for s in pc.ls(type="shadingEngine"):
        if s.hasAttr("staticUid"):
            suid_map[s.staticUid.get()] = s
    return suid_map
    
    
def update_static_Uid_map():
    get_staticUid_map(True)


def add_staticUid(node):
    """Adds attribute 'staticUid' to given node.
    staticUid contains a non-chaning unique identifier string
    useful for identifying nodes between im- and exports.
    (Mayas native uid attribute will change upon exports...) 
    """
    if node.hasAttr("staticUid"):
        return
    node.addAttr("staticUid", dt="string")
    node.staticUid.set(str(uuid4()))


def get_shader_assignment(shape):
    """Reads shader assignment of shape.
    Returns a dict of structure {"<staticUid>": [face indices]}
    The face indices list will be empty if the shader is assigned to the complete shape.
    """
    shading_groups = list(set(shape.connections(type="shadingEngine")))
    assignment_info = {}
    for shading_group in shading_groups:
        members = shading_group.members()
        faces = None
        for mf in members:
            if not mf.startswith(shape.name()):
                continue
            faces = None
            if isinstance(mf, pc.nodetypes.Mesh):
                faces = []
            elif isinstance(mf, pc.general.MeshFace):
                faces = [int(f.split("[")[-1][:-1]) for f in pc.ls(mf, flatten=True)]
            else:
                print("Shape '{}' not of type 'Mesh'. Skipped.")
                return
            add_staticUid(shading_group)
            assignment_info[shading_group.staticUid.get()] = faces
    return assignment_info
    

def write_shader_assignment(shape):
    """Write a dictionary returned by function "get_shader_assignment"
    to an attribute named "shaderAssignments" on the given shape.
    """
    sg_assignment_dict = get_shader_assignment(shape)
    if not sg_assignment_dict:
        return
    if not shape.hasAttr("shaderAssignments"):
        shape.addAttr("shaderAssignments", dt="string")
    shape.shaderAssignments.set(json.dumps(sg_assignment_dict))


def reassign_shaders(shape, namespace=""):
    """Assign shaders by reading info in attribute "shaderAssignments" written
    by function "write_shader_assignent".
    if "namespace" is not empty it will be added to shading group name.
    """
    if not shape.hasAttr("shaderAssignments"):
        return
    sg_assignment = json.loads(shape.shaderAssignments.get())
    for staticUid, faces_list in sg_assignment.items():
        sg = get_staticUid_map().get(staticUid, None)
        if not sg:
            continue
        sg_string = "{}:{}".format(namespace, sg.name())
        if faces_list:
            pc.sets(sg_string, forceElement=shape.f[faces_list])
            continue
        pc.sets(sg_string, forceElement=shape)
