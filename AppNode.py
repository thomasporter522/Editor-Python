from ExpressionNode import ExpressionNode
from FunNode import FunNode
from TypeNode import TypeNode
from HoleNode import HoleNode
from Enums import *
from Merger import unify


class AppNode(ExpressionNode):
    f, x = None, None
    default_rotation = Rotation.INLINE

    forwards = False

    allowed_holes = [HoleType.ANY, HoleType.FUNCTION, HoleType.TYPE]

    def instance(self, node_type):
        return (node_type == NodeType.AppNode)

    def set_children(self, children):
        self.f = children[0]
        self.x = children[1]

    def get_children(self):
        return [self.f, self.x]

    def can_rotate(self):
        return True

    def left_child(self):
        if self.forwards:
            return self.x
        return self.f

    def right_child(self):
        if self.forwards:
            return self.f
        return self.x

    def get_positions(self):
        return self.left_child().get_positions() + self.right_child().get_positions()

    def has_parens(self):
        return self.right_child().instance(NodeType.AppNode) and self.rotation == Rotation.INLINE and self.right_child().rotation == Rotation.INLINE

    def all_apps(self):
        return self.x.all_apps() and self.f.all_apps()

    def rotator_child(self):
        return self.right_child()

    def replace_child(self, old_child, new_child):
        new_child.parent = self
        if self.f == old_child:
            self.f = new_child
        if self.x == old_child:
            self.x = new_child

    def set_directions(self):
        self.f.direction = Direction.FREE
        self.x.direction = Direction.FREE

    def set_holetypes(self):
        self.f.holetype = HoleType.FUNCTION
        self.x.holetype = HoleType.ANY

    def set_coordinates(self, renderer, x, y, node_of_coords):

        if self.rotation == Rotation.INLINE:
            px, py = x + self.anchor_width(renderer) + \
                self.left_child().get_width(renderer), y
            self.coordinate_rect = (px, py, 1, 1)
            node_of_coords.set(px, py, self)

            self.left_child().set_coordinates(
                renderer, *self.head_coords(renderer, x, y), node_of_coords)
            self.right_child().set_coordinates(
                renderer, *self.right_coords(renderer, x, y), node_of_coords)

        elif self.rotation == Rotation.NEWLINE:
            self.coordinate_rect = (x, y, 1, 1)
            node_of_coords.set(x, y, self)
            head, chain = self.get_head_and_chain()
            head.set_coordinates(
                renderer, *self.head_coords(renderer, x, y), node_of_coords)

            cx, cy = self.chain_coords(renderer, x, y, head, chain)
            for i in range(len(chain)):
                px, py = cx[i] - renderer.pipeline_width, cy[i]
                p = chain[i].parent
                node_of_coords.set(px, py, p)
                # if p != self:
                #     p.coordinate_rect = (px, py, 1, 1)

                chain[i].set_coordinates(
                    renderer, cx[i], cy[i], node_of_coords)

    def right_coords(self, renderer, x, y):
        assert (self.rotation == Rotation.INLINE)
        return (x + self.anchor_width(renderer) + renderer.pipeline_width + self.paren_width(renderer) + self.left_child().get_width(renderer), y)

    def get_head_and_chain(self):
        current = self
        result = []
        while (current.instance(NodeType.AppNode) and current.rotation == Rotation.NEWLINE and current.forwards == self.forwards):
            result.append(current.right_child())
            current = current.left_child()
        return (current, result[::-1])

    def get_height(self):
        if self.rotation == Rotation.INLINE:
            return max(self.f.get_height(), self.x.get_height())
        elif self.rotation == Rotation.NEWLINE:
            return self.f.get_height() + self.x.get_height()

    def get_width(self, renderer):
        if self.rotation == Rotation.INLINE:
            result = self.anchor_width(renderer) + renderer.pipeline_width + \
                self.f.get_width(renderer) + self.x.get_width(renderer)
            if self.has_parens():
                result += 2 * renderer.paren_width
            return result
        elif self.rotation == Rotation.NEWLINE:
            head, chain = self.get_head_and_chain()
            chain_widths = [item.get_width(renderer) for item in chain]
            return renderer.anchor_width + max(head.get_width(renderer), renderer.pipeline_width + max(chain_widths))

    def head_coords(self, renderer, x, y):
        return (x+self.anchor_width(renderer), y)

    def chain_coords(self, renderer, x, y, head=None, chain=None):
        if head is None:
            head, chain = self.get_head_and_chain()
        current_height = head.get_height()
        resultx, resulty = [], []
        for item in chain:
            resultx.append(x + renderer.anchor_width + renderer.pipeline_width)
            resulty.append(y + current_height)
            current_height += item.get_height()
        return (resultx, resulty)

    def render(self, renderer, tile, x, y):
        hx, hy = self.head_coords(renderer, x, y)

        if self.rotation == Rotation.INLINE:
            rx, ry = self.right_coords(renderer, x, y)
            px, py = x + self.anchor_width(renderer) + \
                self.left_child().get_width(renderer), y
            renderer.draw_pipeline(tile, px, py, backwards=(not self.forwards))
            if self.has_parens():
                renderer.draw_parens(tile, rx - renderer.paren_width, ry, rx +
                                     self.right_child().get_width(renderer) - renderer.paren_width, ry)
            self.left_child().render(renderer, tile, hx, hy)
            self.right_child().render(renderer, tile, rx, ry)

        elif self.rotation == Rotation.NEWLINE:
            head, chain = self.get_head_and_chain()
            head.render(renderer, tile, hx, hy)
            cx, cy = self.chain_coords(renderer, x, y, head, chain)
            renderer.draw_centered_line(tile, x, y, x, cy[-1])
            for i in range(len(chain)):
                px, py = cx[i] - renderer.pipeline_width, cy[i]
                renderer.draw_exact_line(
                    tile, px - renderer.anchor_width + 0.5, py + 0.5, px + 0.25, py + 0.5)
                renderer.draw_pipeline(
                    tile, px, py, backwards=(not self.forwards))
                chain[i].render(renderer, tile, cx[i], cy[i])

        if self.has_anchor():
            renderer.draw_anchor(tile, x, y)

        self.render_active(renderer, tile, x, y)

    def to_ocaml(self):
        f_ocaml = self.f.to_ocaml()
        x_ocaml = self.x.to_ocaml()
        return "(" + f_ocaml + " " + x_ocaml + ")"

    def compute_inferred_type(self):
        super().compute_inferred_type()
        ft = self.f.inferred_type
        if ft.instance(NodeType.HoleNode):
            self.inferred_type = HoleNode()
        else:
            self.inferred_type = ft.b

    def compute_goal(self):
        ft, xt = self.f.inferred_type, self.x.inferred_type

        fxtype = HoleNode()
        fbtype = HoleNode()
        if not ft.instance(NodeType.HoleNode):
            fxtype = ft.x.t
            fbtype = ft.b

        fmerge = unify(self.goal, fbtype)
        xmerge = unify(xt, fxtype)

        fgoal = FunNode(
            [TypeNode([HoleNode(), xmerge["result"]]), fmerge["result"]], reference_children=True)

        self.f.goal = fgoal
        self.x.goal = xmerge["result"]

        self.happy = fmerge["successful"] and xmerge["successful"]

        super().compute_goal()

    def type_infer(self, context):
        self.context = context 
        self.x.type_infer(context)
        self.f.type_infer(context)
        self.type = self.f.type.reduce_and_equate(self.x.type)
        if self.type is None:
            self.type = HoleNode()

    def reduce_and_equate(self, x_type):
        assert False, "not implemented"


