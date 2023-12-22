from ExpressionNode import ExpressionNode
from IdNode import IdNode
from Enums import *

class UniverseNode(ExpressionNode):
  def __init__(self, n = 0):
    self.n = n
    self.id_node = IdNode("Type")

  def instance(self, node_type):
    return (node_type == NodeType.UniverseNode)

  def set_coordinates(self, renderer, x, y, node_of_coords):
    i = 0
    while i < self.get_width(renderer):
        node_of_coords.set(x + i, y, self)
        i += 1
    self.coordinate_rect = (x + i, y, 1, 1)

  def get_heigth(self):
    return self.id_node.get_height()

  def get_width(self, renderer):
    return self.id_node.get_width(renderer)

  def render(self, renderer, tile, x, y):
    return self.id_node.render(renderer, tile, x, y)

  def to_ocaml(self):
    return "Type"