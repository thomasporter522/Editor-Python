from ExpressionNode import ExpressionNode
from Enums import *


class EqualityNode(ExpressionNode):
    x, y = None, None
    default_rotation = Rotation.INLINE

    allowed_holes = [HoleType.ANY, HoleType.TYPE]

    def instance(self, node_type):
        return (node_type == NodeType.EqualityNode)

    def set_children(self, children):
        self.x = children[0]
        self.y = children[1]

    def get_children(self):
        return [self.x, self.y]

    def replace_child(self, old_child, new_child):
        new_child.parent = self
        if self.x == old_child:
            self.x = new_child
        if self.y == old_child:
            self.y = new_child

    def set_directions(self):
        self.f.direction = Direction.FREE
        self.x.direction = Direction.FREE
