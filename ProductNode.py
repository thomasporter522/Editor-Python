from ExpressionNode import ExpressionNode
from Enums import *


class ProductNode(ExpressionNode):
    children = None
    fields = None
    default_rotation = Rotation.INLINE

    allowed_holes = [HoleType.ANY, HoleType.TYPE]

    def instance(self, node_type):
        return (node_type == NodeType.ProductNode)

    def can_rotate(self):
        return True

    def rotator_child(self):
        return None

    def set_children(self, children):
        self.children = children

    def get_children(self):
        return self.children

    def set_directions(self):
        for child in self.children:
            child.direction = Direction.FREE
        for field in self.fields:
            field.direction = Direction.BOUND

    def set_holetypes(self):
        for child in self.children:
            child.holetype = HoleType.ANY
        for field in self.fields:
            field.holetype = HoleType.NEWLITERAL

    def replace_child(self, old_child, new_child):
        new_child.parent = self
        for i in range(len(self.children)):
            if self.children[i] == old_child:
                self.children[i] = new_child

    def set_directions(self):
        for child in self.children:
            child.direction = Direction.FREE

    def render_entry(self, renderer, tile, x, y, i, field_widths):
        self.fields[i].render(renderer, tile, x, y)
        renderer.draw_arrow(tile, x + field_widths[i], y, backwards=True)
        self.children[i].render(
            renderer, tile, x + field_widths[i] + renderer.arrow_width, y)

    def render(self, renderer, tile, x, y):
        field_widths = self.field_widths(renderer)
        field_coords = self.field_coords(renderer, x, y)
        for i in range(len(self.children)):
            self.render_entry(renderer, tile, *
                              field_coords[i], i, field_widths)
