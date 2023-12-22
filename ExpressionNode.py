

from Enums import *


class ExpressionNode():

    context = None
    inferred_type = None
    goal = None
    happy = True

    def __init__(self, children, replacing=None,  permanent=False, reference_children=False):

        self.set_children(children)
        if not reference_children:
            for child in children:
                child.parent = self

        self.permanent = permanent
        self.active = False
        self.rotation = Rotation.default
        self.coordinate_rect = None

        if replacing is not None:
            assert (self.can_replace(replacing))
            self.replace(replacing)
        else:
            self.holetype = HoleType.default
            self.direction = Direction.default

        self.refresh()

    def must_be_flat(self):
        p = self.parent
        if not p.instance(NodeType.RootNode) and p.must_be_flat():
            return True
        if p.instance(NodeType.AppNode):
            if p.rotation != Rotation.INLINE:
                return False
            if self == p.left_child():
                return True
            if p.has_parens():
                return True
            return False
        if p.instance(NodeType.ProductNode):
            return p.rotation == Rotation.INLINE
        if p.instance(NodeType.TypeNode):
            return True
        return False

    def can_replace(self, node):
        inline_issue = (not self.all_flat()) and node.must_be_flat()
        return (not inline_issue) and node.holetype in self.allowed_holes

    def replace(self, replacing):
        replacing.parent.replace_child(replacing, self)
        self.holetype = replacing.holetype
        self.direction = replacing.direction

    def refresh(self):
        # self.set_local_context()
        # self.set_goals()
        self.set_holetypes()
        self.set_directions()

    def get_positions(self):
        result = []
        for child in self.get_children():
            result += child.get_positions()
        return result

    def all_flat(self):

        if self.rotation != Rotation.INLINE:
            return False

        for child in self.get_children():
            if not child.all_flat():
                return False

        return True

    def set_children(self, children):
        pass

    def get_children(self):
        return []

    def set_directions(self):
        pass

    def set_invisible(self):
        self.coordinate_rect = None
        for child in self.get_children():
            child.set_invisible()

    def visible(self):
        return (self.coordinate_rect is not None)

    def can_collapse(self):
        return False

    def can_rotate(self):
        return False

    def all_apps(self):
        return False

    def has_anchor(self):
        return (self.rotation == Rotation.NEWLINE or self.direction == Direction.BOUND)

    def anchor_width(self, renderer):
        if self.has_anchor():
            return renderer.anchor_width
        return 0

    def has_parens(self):
        return False

    def paren_width(self, renderer):
        if self.has_parens():
            return renderer.paren_width
        return 0

    def render_active(self, renderer, tile, x, y):
        if self.active:
            renderer.draw_selection_rect(
                tile, x, y, self.get_width(renderer), self.get_height())

    def compute_context(self, context):
        self.context = context
        for child in self.get_children():
            child.compute_context(context)

    def compute_inferred_type(self):
        for child in self.get_children():
            child.compute_inferred_type()

    def compute_goal(self):
        for child in self.get_children():
            child.compute_goal()
            self.happy = self.happy and child.happy

    # If you are an APP node, beta reduce until you are a function type. 
    # Then make sure that your input type matches [x_type]
    # If this can't be done (you are not an app or function), return None. 
    def reduce_and_equate(self, x_type):
        return None