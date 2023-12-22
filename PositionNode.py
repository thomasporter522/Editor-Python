from ExpressionNode import ExpressionNode
from Enums import *


class PositionNode(ExpressionNode):
    allowed_holes = [HoleType.ANY, HoleType.FUNCTION,
                     HoleType.NEWLITERAL, HoleType.TYPE]

    def __init__(self, replacing=None,  permanent=False):
        super().__init__(children=[], replacing=replacing, permanent=permanent)
        self.next = self
        self.last = self

    def instance(self, node_type):
        return (node_type == NodeType.PositionNode)

    def set_holetypes(self):
        pass

    def get_positions(self):
        return [self]

    def all_apps(self):
        return True
