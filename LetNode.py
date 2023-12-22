from ExpressionNode import ExpressionNode
from HoleNode import HoleNode
from Enums import *


class LetNode(ExpressionNode):
    x, y, b = None, None, None
    default_rotation = Rotation.NEWLINE
    collapsed = False

    allowed_holes = [HoleType.ANY]

    def instance(self, node_type):
        return (node_type == NodeType.LetNode)

    def set_children(self, children):
        self.x = children[0]
        self.y = children[1]
        self.b = children[2]

    def get_children(self):
        return [self.x, self.y, self.b]

    def replace_child(self, old_child, new_child):
        new_child.parent = self
        if self.x == old_child:
            self.x = new_child
        if self.y == old_child:
            self.y = new_child
        if self.b == old_child:
            self.b = new_child

    def set_directions(self):
        self.x.direction = Direction.FREE
        self.y.direction = Direction.BOUND
        self.b.direction = Direction.BOUND

    def set_holetypes(self):
        self.x.holetype = HoleType.NEWLITERAL
        self.y.holetype = HoleType.ANY
        self.b.holetype = HoleType.ANY

    def all_flat(self):
        return False

    def set_coordinates(self, renderer, x, y, node_of_coords):

        self.coordinate_rect = (x, y, 1, 1)
        node_of_coords.set(x, y, self)

        self.x.set_coordinates(
            renderer, *self.x_coords(renderer, x, y), node_of_coords)
        self.b.set_coordinates(
            renderer, *self.b_coords(renderer, x, y), node_of_coords)

        if not self.collapsed:
            self.y.set_coordinates(
                renderer, *self.y_coords(renderer, x, y), node_of_coords)

    def can_collapse(self):
        return True

    def can_rotate(self):
        return True

    def rotator_child(self):
        return self.y

    def get_header_width(self, renderer):
        return renderer.anchor_width\
            + renderer.arrow_width\
            + self.x.get_width(renderer)

    def get_width(self, renderer, full=True):

        upper_width = 0

        if self.collapsed:
            upper_width = self.get_header_width(
                renderer) + renderer.ellipsis_width
        elif self.rotation == Rotation.INLINE:
            upper_width = self.get_header_width(
                renderer) + self.y.get_width(renderer)
        elif self.rotation == Rotation.NEWLINE:
            upper_width = max(self.get_header_width(renderer),
                              renderer.anchor_width +
                              self.y.get_width(renderer))

        if full:
            return max(self.b.get_width(renderer), upper_width)

        return upper_width

    def get_height(self):
        if self.collapsed:
            return 1 + self.b.get_height()
        if self.rotation == Rotation.INLINE:
            return 1 + self.b.get_height() + max(0, self.y.get_height()-1)
        elif self.rotation == Rotation.NEWLINE:
            return 1 + self.b.get_height() + self.y.get_height()

    def x_coords(self, renderer, x, y):
        return (x + renderer.anchor_width, y)

    def y_coords(self, renderer, x, y):
        if self.rotation == Rotation.NEWLINE:
            return (x + renderer.anchor_width, y+1)
        elif self.rotation == Rotation.INLINE:
            return (x+self.get_header_width(renderer), y)

    def b_coords(self, renderer, x, y):
        by = y
        if self.collapsed or self.rotation == Rotation.NEWLINE:
            by += 1
        if not self.collapsed:
            by += self.y.get_height()
        return (x, by)

    def render(self, renderer, tile, x, y):

        xx, xy = self.x_coords(renderer, x, y)
        if not self.collapsed:
            yx, yy = self.y_coords(renderer, x, y)
        bx, by = self.b_coords(renderer, x, y)

        x_width = self.x.get_width(renderer)

        renderer.draw_centered_line(tile, x, y, bx, by)
        renderer.draw_anchor(tile, x, y)
        renderer.draw_arrow(tile, xx + x_width, y, backwards=True)
        if self.rotation == Rotation.INLINE and not self.collapsed:
            renderer.draw_centered_line(
                tile, x + x_width + renderer.arrow_width, y, yx, yy)

        if self.collapsed:
            renderer.draw_ellipsis(
                tile, xx + x_width + renderer.arrow_width, y)
        else:
            if self.rotation == Rotation.NEWLINE and renderer.let_supported:
                renderer.draw_centered_line(tile, x, yy, yx, yy)
            self.y.render(renderer, tile, yx, yy)

        self.x.render(renderer, tile, xx, xy)
        self.b.render(renderer, tile, bx, by)
        self.render_active(renderer, tile, x, y)

    def to_ocaml(self):
        x_ocaml = self.x.to_ocaml()
        y_ocaml = self.y.to_ocaml()
        b_ocaml = self.b.to_ocaml()
        return "(let " + x_ocaml + " = " + y_ocaml + " in " + b_ocaml + ")"

    def compute_context(self, context):
        self.context = context
        self.x.compute_context(context)
        self.y.compute_context(context)
        self.b.compute_context(context + [self.x])

    def compute_inferred_type(self):
        super().compute_inferred_type()
        self.inferred_type = self.b.inferred_type

    def compute_goal(self):
        self.b.goal = self.goal 
        self.y.goal = self.x.t
        self.x.goal = HoleNode()
        self.happy = True
        super().compute_goal()