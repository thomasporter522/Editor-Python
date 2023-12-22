from PositionNode import PositionNode
from Enums import *


class HoleNode(PositionNode):

    mirror = None

    def instance(self, node_type):
        return (node_type == NodeType.HoleNode or node_type == NodeType.PositionNode)

    def set_coordinates(self, renderer, x, y, node_of_coords):
        self.coordinate_rect = (x, y, 1, 1)
        node_of_coords.set(x, y, self)

    def get_width(self, renderer):
        return renderer.hole_width

    def get_height(self):
        return 1

    def render(self, renderer, tile, x, y):
        if self.mirror is None:
            renderer.draw_hole(tile, x, y, active=self.active)
        elif self.active:
            print("mirroring")

    def to_ocaml(self):
        if self.active:
            return "▮"
        return "_"

    # def compute_inferred_type(self):
    #     self.inferred_type = HoleNode()

    def type_infer(self, context):
        self.context = context
        self.type = HoleNode()
