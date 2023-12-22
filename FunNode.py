from ExpressionNode import ExpressionNode
from TypeNode import TypeNode
from HoleNode import HoleNode
from UniverseNode import UniverseNode
from Enums import *


class FunNode(ExpressionNode):
    x, b = None, None
    collapsed = False
    default_rotation = Rotation.NEWLINE

    allowed_holes = [HoleType.ANY, HoleType.FUNCTION, HoleType.TYPE]

    def instance(self, node_type):
        return (node_type == NodeType.FunNode)

    def set_children(self, children):
        self.x = children[0]
        self.b = children[1]

    def get_children(self):
        return [self.x, self.b]

    def replace_child(self, old_child, new_child):
        new_child.parent = self
        if self.x == old_child:
            self.x = new_child
        if self.b == old_child:
            self.b = new_child

    def set_directions(self):
        self.x.direction = Direction.FREE
        if self.rotation == Rotation.INLINE:
            self.b.direction = Direction.FREE
        else:
            self.b.direction = Direction.BOUND

    def set_holetypes(self):
        self.x.holetype = HoleType.NEWLITERAL
        self.b.holetype = HoleType.ANY

    def set_coordinates(self, renderer, x, y, node_of_coords):
        self.coordinate_rect = (x, y, 1, 1)
        node_of_coords.set(x, y, self)

        self.x.set_coordinates(
            renderer, *self.x_coords(renderer, x, y), node_of_coords)
        self.b.set_coordinates(
            renderer, *self.b_coords(renderer, x, y), node_of_coords)

    def can_collapse(self):
        return False

    def can_rotate(self):
        return True

    def rotator_child(self):
        return self.b

    def get_height(self):
        if self.rotation == Rotation.INLINE:
            return max(self.x.get_height(), self.b.get_height())
        elif self.rotation == Rotation.NEWLINE:
            return 1 + self.b.get_height()

    def get_width(self, renderer):
        if self.rotation == Rotation.INLINE:
            return self.anchor_width(renderer) + self.x.get_width(renderer) + renderer.arrow_width + self.b.get_width(renderer)
        elif self.rotation == Rotation.NEWLINE:
            return max(self.anchor_width(renderer) + self.x.get_width(renderer) + renderer.arrow_width, self.b.get_width(renderer))

    def x_coords(self, renderer, x, y):
        return (x + self.anchor_width(renderer), y)

    def b_coords(self, renderer, x, y):
        if self.rotation == Rotation.INLINE:
            return (x + self.anchor_width(renderer) + renderer.arrow_width + self.x.get_width(renderer), y)
        elif self.rotation == Rotation.NEWLINE:
            return (x, y + 1)

    def render(self, renderer, tile, x, y):
        xx, xy = self.x_coords(renderer, x, y)
        bx, by = self.b_coords(renderer, x, y)

        x_width = self.x.get_width(renderer)

        if self.rotation == Rotation.NEWLINE:
            renderer.draw_centered_line(tile, x, y, bx, by)
        if self.has_anchor():
            renderer.draw_anchor(tile, x, y)
        renderer.draw_arrow(tile, xx + x_width, y)

        self.x.render(renderer, tile, xx, xy)
        self.b.render(renderer, tile, bx, by)
        self.render_active(renderer, tile, x, y)

    def to_ocaml(self):
        x_ocaml = self.x.to_ocaml()
        b_ocaml = self.b.to_ocaml()
        return "(fun " + x_ocaml + " -> " + b_ocaml + ")"

    # def compute_context(self, context):
    #     self.context = context
    #     self.x.compute_context(context)
    #     self.b.compute_context(context + [self.x])

    # def compute_inferred_type(self):
    #     super().compute_inferred_type()
    #     self.inferred_type = FunTypeNode([self.x, self.b.inferred_type],
    #                                      reference_children=True)

    # def compute_goal(self):
    #     self.x.goal = HoleNode()

    #     if not self.goal.instance(NodeType.FunNode):
    #         self.b.goal = HoleNode()
    #         self.happy = self.goal.instance(NodeType.HoleNode)
    #     else:
    #         self.b.goal = self.goal.b
    #         self.happy = True

    #     super().compute_goal()

    def type_infer(self, context):
        self.context = context
        self.x.type_infer(context)
        self.b.type_infer(context + [self.x])
        self.type = FunTypeNode([self.x.type, self.b.type], reference_children=True)

class FunTypeNode(FunNode):

    # def compute_inferred_type(self):
    #     super().super().compute_inferred_type()
    #     self.inferred_type = UniverseNode()

    # def compute_goal(self):
    #     self.x.goal = HoleNode()
    #     if self.fun_type:
    #         self.b.goal = UniverseNode()
    #         self.happy = True
    #     return super().super().compute_goal()

    def type_infer(self, context):
        self.context = context
        self.type = UniverseNode()

    def reduce_and_equate(self, x_type):
        equate(self.b, x_type)