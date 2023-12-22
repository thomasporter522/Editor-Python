from ExpressionNode import ExpressionNode
from UniverseNode import UniverseNode
from Enums import *


class TypeNode(ExpressionNode):

    allowed_holes = [HoleType.NEWLITERAL]

    def instance(self, node_type):
        return (node_type == NodeType.TypeNode)

    def set_children(self, children):
        self.x = children[0]
        self.t = children[1]

    def get_children(self):
        return [self.x, self.t]

    def replace_child(self, old_child, new_child):
        new_child.parent = self
        if self.x == old_child:
            self.x = new_child
        if self.t == old_child:
            self.t = new_child

    def set_directions(self):
        self.x.direction = Direction.FREE
        self.t.direction = Direction.FREE

    def set_holetypes(self):
        self.x.holetype = HoleType.NEWLITERAL
        if self.x.instance(NodeType.IdNode):
            self.x.binding = True
        self.t.holetype = HoleType.TYPE

    def set_coordinates(self, renderer, x, y, node_of_coords):
        symbolx, symboly = self.symbol_coords(renderer, x, y)

        self.coordinate_rect = (symbolx, symboly, 1, 1)
        node_of_coords.set(symbolx, symboly, self)

        self.x.set_coordinates(
            renderer, *self.x_coords(renderer, x, y), node_of_coords)
        self.t.set_coordinates(
            renderer, *self.t_coords(renderer, x, y), node_of_coords)

    def has_parens(self):
        return not self.t.all_apps()

    def get_height(self):
        return 1

    def get_width(self, renderer):
        result = self.x.get_width(
            renderer) + renderer.colon_width + self.t.get_width(renderer)
        if self.has_parens():
            result += 2 * renderer.paren_width
        return result

    def x_coords(self, renderer, x, y):
        return (x, y)

    def symbol_coords(self, renderer, x, y, x_width=None):
        if x_width is None:
            x_width = self.x.get_width(renderer)
        return (x + x_width, y)

    def t_coords(self, renderer, x, y, x_width=None):
        if x_width is None:
            x_width = self.x.get_width(renderer)
        result = x + x_width + renderer.colon_width
        if self.has_parens():
            result += renderer.paren_width
        return (result, y)

    def render(self, renderer, tile, x, y):
        xx, xy = self.x_coords(renderer, x, y)
        symbolx, symboly = self.symbol_coords(renderer, x, y)
        tx, ty = self.t_coords(renderer, x, y)
        self.x.render(renderer, tile, xx, xy)
        renderer.draw_colon(tile, symbolx, symboly)
        if self.has_parens():
            renderer.draw_parens(tile, tx - renderer.paren_width, ty,
                                 tx + self.t.get_width(renderer) - renderer.paren_width, ty)
        self.t.render(renderer, tile, tx, ty)
        self.render_active(renderer, tile, x, y)

    def to_ocaml(self):
        x_ocaml = self.x.to_ocaml()
        t_ocaml = self.t.to_ocaml()

        return "(" + x_ocaml + " : " + t_ocaml + ")"

    def compute_goal(self):
        self.x.goal = self.goal
        self.t.goal = UniverseNode()
        self.happy = True
        self.x.compute_goal()
        self.t.compute_goal()
        self.happy = self.t.happy
