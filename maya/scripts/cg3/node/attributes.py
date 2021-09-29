def connect_object_attributes(from_objs, from_attrs, to_objs, to_attrs):
    """
    lame
    """
    for f, t in zip(from_objs, to_objs):
        for from_attr, to_attr in zip(from_attrs, to_attrs):
            f.attr(from_attr) >> t.attr(to_attr)
