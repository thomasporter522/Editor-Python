from Enums import NodeType, Rotation, HoleType
from HoleNode import HoleNode
from LetNode import LetNode
from TypeNode import TypeNode
from IdNode import IdNode
from FunNode import FunNode
from AppNode import AppNode


class Command:

    def allowed(self, expression):
        assert False

    def do(self, expression):
        assert False

    def do_if_allowed(self, expression):
        if self.allowed(expression):
            self.do(expression)


class Undo(Command):
    pass


class Redo(Command):
    pass


def filter_valid(positions, hole_only):
    positions = [p for p in positions if p.visible()]
    if hole_only:
        positions = [p for p in positions if p.instance(NodeType.HoleNode)]
    return positions


class Cycle(Command):
    hole_only = False

    def __init__(self, hole_only=False):
        self.hole_only = hole_only
        self.positions = None

    def allowed(self, expression):
        if not expression.active_node.instance(NodeType.PositionNode):
            return False
        self.positions = filter_valid(
            expression.get_positions(), self.hole_only)
        if len(self.positions) > 1:
            return True
        if len(self.positions) == 0:
            return False
        return expression.active_node != self.positions[0]


class FrontCycle(Cycle):

    def do(self, expression):
        if expression.active_node != self.positions[0]:
            expression.set_active_node(self.positions[0])
            return
        expression.set_active_node(self.positions[1])


class BackCycle(Cycle):

    def do(self, expression):
        if len(self.positions) == 1:
            expression.set_active_node(self.positions[0])
            return
        expression.set_active_node(self.positions[-1])


class GoDown(Command):

    def __init__(self, hole_only=False):
        self.hole_only = hole_only
        self.positions = None

    def allowed(self, expression):
        self.positions = filter_valid(
            expression.active_node.get_positions(), self.hole_only)
        return len(self.positions) > 0

    def do(self, expression):
        expression.set_active_node(self.positions[0])


class GoTop(Command):

    def allowed(self, expression):
        return not expression.active_node.parent.instance(NodeType.RootNode)

    def do(self, expression):
        expression.set_active_node(expression.head.x)


class GoUp(Command):

    def __init__(self, full=False):
        self.target_node = None

    def allowed(self, expression):
        current = expression.active_node
        # if current.instance(NodeType.LetNode) and (not current.full_select):
        #     return True
        current = current.parent
        while (not current.visible() and not current.instance(NodeType.RootNode)):
            current = current.parent
        if current.instance(NodeType.RootNode):
            return False
        self.target_node = current
        return True

    def do(self, expression):
        expression.set_active_node(self.target_node)


class Delete(Command):

    def allowed(self, expression):
        if expression.active_node.permanent:
            return False
        if expression.active_node.instance(NodeType.HoleNode):
            return False
        return True

    def do(self, expression):
        n = HoleNode()
        Add(n, overwrite=True).do(expression)
        expression.set_active_node(n)


class Add(Command):

    def __init__(self, node, overwrite=False):
        self.node = node
        self.overwrite = overwrite

    def allowed(self, expression):
        if not self.overwrite and not expression.active_node.instance(NodeType.HoleNode):
            return False
        return self.node.can_replace(expression.active_node)

    def do(self, expression):
        self.node.replace(expression.active_node)
        expression.refresh_positions()
        expression.set_active_node(self.node)


class Cut(Command):

    def __init__(self):
        self.delete_command = None

    def allowed(self, expression):
        self.delete_command = Delete()
        return self.delete_command.allowed(expression)

    def do(self, expression):
        expression.clipboard = expression.active_node
        self.delete_command.do(expression)


class Paste(Command):

    def __init__(self):
        self.add_command = None

    def allowed(self, expression):
        if expression.clipboard is None:
            return False
        self.add_command = Add(expression.clipboard)
        return self.add_command.allowed(expression)

    def do(self, expression):
        self.add_command.do(expression)
        expression.clipboard = None


class SelectNode(Command):

    def __init__(self, node):
        self.node = node

    def allowed(self, expression):
        return (expression.active_node != self.node)

    def do(self, expression):
        expression.set_active_node(self.node)


class LetDelete(Command):
    pass

# class AddType(Command):

#     def __init__(self):
#         n = TypeNode([HoleNode(), HoleNode()])
#         return Add(n)


class AddNode(Command):

    active_node = None

    def __init__(self, node, overwrite=False):
        self.node = node
        self.add_command = Add(node, overwrite)

    def allowed(self, expression):
        return self.add_command.allowed(expression)

    def do(self, expression):
        self.add_command.do(expression)
        if self.active_node is not None:
            expression.set_active_node(self.active_node)


class AddLet(AddNode):
    def __init__(self, overwrite=False):
        active_node = HoleNode()
        super().__init__(
            LetNode([TypeNode([HoleNode(), HoleNode()], permanent=True), active_node, HoleNode()]), overwrite)
        self.active_node = active_node


class AddId(AddNode):
    def __init__(self, id):
        super().__init__(IdNode(id))


class AddFun(AddNode):
    def __init__(self, overwrite=False):
        active_node = HoleNode()
        n = FunNode(
            [TypeNode([HoleNode(), HoleNode()], permanent=True), active_node])
        super().__init__(n, overwrite)
        self.active_node = active_node

    def do(self, expression):
        super().do(expression)
        if self.node.holetype == HoleType.TYPE:
            self.node.fun_type = True


class AddApp(AddNode):
    def __init__(self, forwards=True, overwrite=False):
        n = AppNode([HoleNode(), HoleNode()])
        n.forwards = forwards
        active_node = n.left_child()
        super().__init__(n, overwrite)
        self.active_node = active_node


class TypeId(Command):

    def __init__(self, id):
        self.id = id

    def allowed(self, expression):
        return expression.active_node.instance(NodeType.IdNode)

    def do(self, expression):
        expression.active_node.id += self.id


class Backspace(Command):

    def allowed(self, expression):
        return expression.active_node.instance(NodeType.IdNode) and len(expression.active_node.id) > 1

    def do(self, expression):
        expression.active_node.id = expression.active_node.id[:-1]


class Rotate(Command):

    def __init__(self, back_only=False):
        self.back_only = back_only
        self.rotator = None

    def allowed_to_rotate(self, node):
        if not node.can_rotate():
            return False
        if node.can_collapse() and node.collapsed:
            return False
        if node.rotation == Rotation.INLINE and self.back_only:
            return False
        if node.must_be_flat():
            return False
        if node.instance(NodeType.AppNode) and (not node.left_child().all_flat()):
            return False
        return True

    def allowed(self, expression):
        current = expression.active_node
        if self.allowed_to_rotate(current):
            self.rotator = current
            return True
        if not self.allowed_to_rotate(current.parent):
            return False
        if not current.instance(NodeType.HoleNode):
            return False
        if not current == current.parent.rotator_child():
            return False
        self.rotator = current.parent
        return True

    def do(self, expression):
        self.rotator.rotation = Rotation.other(self.rotator.rotation)
        self.rotator.set_directions()


class Reverse(Command):

    def allowed(self, expression):
        return expression.active_node.instance(NodeType.AppNode)

    def do(self, expression):
        expression.active_node.forwards = not expression.active_node.forwards
        expression.refresh_positions()


class CollapseLet(Command):

    def allowed(self, expression):
        return expression.active_node.instance(NodeType.LetNode)

    def do(self, expression):
        expression.active_node.collapsed = not expression.active_node.collapsed


class ApplyUpwards(Command):

    def __init__(self, forwards):
        self.forwards = forwards
        self.command = None

    def allowed(self, expression):
        self.command = AddApp(forwards=self.forwards, overwrite=True)
        if not self.command.node.left_child().holetype in expression.active_node.allowed_holes:
            return False
        return self.command.allowed(expression)

    def do(self, expression):
        n = expression.active_node
        self.command.do(expression)
        if not n.all_flat():
            expression.active_node.parent.rotation = Rotation.other(
                expression.active_node.parent.rotation)
        Add(n).do(expression)
        expression.set_active_node(n)
        if not n.instance(NodeType.HoleNode):
            expression.set_active_node(
                expression.active_node.parent.right_child())


class TextCommand(Command):

    def __init__(self):
        self.command = None

    def command_of_text(text):
        if text == "let":
            return AddLet(overwrite=True)
        if text == "fun":
            return AddFun(overwrite=True)

    def allowed(self, expression):
        if not expression.active_node.instance(NodeType.IdNode):
            return False
        self.command = TextCommand.command_of_text(expression.active_node.id)
        if self.command is None:
            return False
        return self.command.allowed(expression)

    def do(self, expression):
        self.command.do(expression)
