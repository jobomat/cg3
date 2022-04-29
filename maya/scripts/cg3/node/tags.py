from collections import defaultdict
from typing import Any

import pymel.core as pc


def tag_node(node, tag_key: str, tag_value: str):
    """Attach attribute named tag_key with tag_value to node."""
    if not node.hasAttr(tag_key):
        node.addAttr(tag_key, dt="string")
    node.attr(tag_key).set(tag_value)


def get_tagged_nodes(tag_key: str, tag_value: str, **kwargs):
    nodes = pc.ls(**kwargs)
    tagged_nodes = []
    for node in nodes:
        if node.hasAttr(tag_key):
            if node.assetTag.get() == tag_value:
                tagged_nodes.append(node)
    return tagged_nodes


def get_tagged_dag_nodes(tag_key: str, tag_value: str):
    return get_tagged_nodes(tag_key, tag_value, dag=True)


def get_tag_dict(tag_key: str, **ls_kwargs):
    node_dict = defaultdict(list)
    for node in pc.ls(**ls_kwargs):
        if node.hasAttr(tag_key):
            node_dict[node.attr(tag_key).get()].append(node)
    return node_dict
