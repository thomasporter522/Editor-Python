from ExpressionNode import ExpressionNode
from Enums import *


class AccessNode(ExpressionNode):
    x, f = None, None
    default_rotation = Rotation.INLINE

    allowed_holes = [HoleType.ANY, HoleType.FUNCTION]

    def instance(self, node_type):
        return (node_type == NodeType.AccessNode)

    def set_children(self, children):
        self.x = children[0]
        self.f = children[1]

    def get_children(self):
        return [self.x, self.f]

    def replace_child(self, old_child, new_child):
        new_child.parent = self
        if self.x == old_child:
            self.x = new_child
        if self.f == old_child:
            self.f = new_child

    def set_directions(self):
        self.x.direction = Direction.FREE
        self.f.direction = Direction.FREE
