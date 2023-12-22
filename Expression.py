
from Enums import Direction, Rotation, HoleType, NodeType


from HoleNode import HoleNode
from RootNode import RootNode
# from IdNode import IdNode


def link(a, b):
    a.next = b
    b.last = a


def link_position_list(positions):
    if len(positions) > 0:
        for i in range(len(positions)-1):
            link(positions[i], positions[i+1])
        link(positions[-1], positions[0])


class CoordinateDirectory:

    def __init__(self):
        self.map = {}

    def set(self, x, y, v):
        self.map[(x, y)] = v

    def valid(self, x, y):
        return (x, y) in self.map.keys()

    def get(self, x, y):
        return self.map[(x, y)]


class Expression:
    def __init__(self, global_context=[], goal=None):
        hole = HoleNode()
        hole.active = True

        self.active_node = hole
        self.head = RootNode([hole])
        self.global_context = global_context

        self.node_of_coords = CoordinateDirectory()
        self.clipboard = None

        self.goal = goal

    def set_active_node(self, node):
        self.active_node.active = False
        self.active_node = node
        self.active_node.active = True

    def refresh_positions(self):
        link_position_list(self.head.get_positions())

    def get_positions(self):
        assert (self.active_node.instance(NodeType.PositionNode))
        current = self.active_node.next
        result = [self.active_node]
        while current != self.active_node:
            result.append(current)
            current = current.next
        return result

    def set_coordinates(self, renderer, x, y):
        self.node_of_coords = CoordinateDirectory()
        self.head.set_invisible()
        self.head.set_coordinates(renderer, x, y, self.node_of_coords)

    def go_up_if_invisible(self):
        current = self.active_node
        while not current.visible():
            current = current.parent
        self.set_active_node(current)
