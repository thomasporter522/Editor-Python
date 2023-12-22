from ExpressionNode import ExpressionNode
from Enums import *


class RootNode(ExpressionNode):

    def instance(self, node_type):
        return (node_type == NodeType.RootNode)

    def set_children(self, children):
        self.x = children[0]

    def get_children(self):
        return [self.x]

    def replace_child(self, old_child, new_child):
        new_child.parent = self
        if self.x == old_child:
            self.x = new_child

    def set_directions(self):
        self.x.direction = Direction.FREE

    def set_holetypes(self):
        self.x.holetype = HoleType.ANY

    def set_coordinates(self, renderer, x, y, node_of_coords):
        self.x.set_coordinates(renderer, x, y, node_of_coords)

    def render(self, renderer, tile, x, y):
        self.x.render(renderer, tile, x, y)
