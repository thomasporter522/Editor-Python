from HoleNode import HoleNode
from Enums import *


def unify(e1, e2):
    if e1.instance(NodeType.HoleNode):
        return {"result": e2, "successful": True, "bindings": []}
    elif e2.instance(NodeType.HoleNode):
        return {"result": e1, "successful": True, "bindings": []}
    return {"result": HoleNode(), "successful": False, "bindings": []}
