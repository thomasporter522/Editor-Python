from ExpressionNode import ExpressionNode
from PositionNode import PositionNode
from HoleNode import HoleNode
from Enums import *


class IdNode(PositionNode):
    def __init__(self, id, binding=False, replacing=None,  permanent=False):
        super().__init__(replacing=replacing, permanent=permanent)
        self.id = id
        self.binding = binding

    def instance(self, node_type):
        return (node_type == NodeType.IdNode or node_type == NodeType.PositionNode)

    def set_coordinates(self, renderer, x, y, node_of_coords):
        i = 0
        while i < self.get_width(renderer):
            node_of_coords.set(x + i, y, self)
            i += 1
        self.coordinate_rect = (x + i, y, 1, 1)

    def get_width(self, renderer):
        return renderer.string_width(self.id) + self.anchor_width(renderer)

    def get_height(self):
        return 1

    def render(self, renderer, tile, x, y):
        if self.has_anchor():
            renderer.draw_anchor(tile, x, y)
        renderer.draw_string(tile, x + self.anchor_width(renderer),
                             y, self.id, self.active)

    def to_ocaml(self):
        return self.id

    # def compute_inferred_type(self):
    #     super().compute_inferred_type()
    #     for item in self.context:
    #         if item.x.instance(NodeType.IdNode) and item.x.id == self.id:
    #             self.inferred_type = item.t
    #             self.happy = (not self.binding)
    #             return
    #     self.inferred_type = HoleNode()
    #     self.happy = self.binding

    def type_infer(self, context):
        self.context = context 
        self.type = HoleNode() 
        for item in self.context:
            if item.x.instance(NodeType.IdNode) and item.x.id == self.id:
                self.type = item.t

