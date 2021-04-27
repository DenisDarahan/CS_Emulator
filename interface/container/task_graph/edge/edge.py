from math import sqrt, asin, pi

from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.uix.tabbedpanel import TabbedPanelItem

from .popups import EdgeAskWeight


class Edge(FloatLayout):
    edge_menu = ObjectProperty()
    edge_button = ObjectProperty()
    vector = ObjectProperty()

    def __init__(self, edge_id: int, edge_weight: int, parent_tab: TabbedPanelItem, src_node, dst_node, **kwargs):
        self.edge_id = edge_id
        self.edge_weight = edge_weight
        self.parent_tab = parent_tab
        self.src_node = src_node
        self.dst_node = dst_node

        super().__init__(**kwargs)
        self.draw_vector()
        self.bind(pos=self.draw_vector)

    def draw_vector(self, *_args):
        distance_x = self.dst_node.pos[0] - self.src_node.pos[0]
        distance_y = self.dst_node.pos[1] - self.src_node.pos[1]
        distance = sqrt(distance_x ** 2 + distance_y ** 2)
        sign_x = distance_x / abs(distance_x) if distance_x else 1

        self.size = (abs(distance_x), abs(distance_y))
        self.edge_button.pos = (self.pos[0] + self.size[0] / 2, self.pos[1] + self.size[1] / 2)

        line = self.vector.canvas.before.get_group('line')[0]
        line.points = (
            self.src_node.pos[0] + 73 + 75 * distance_x / (0 ** distance + distance),
            self.src_node.pos[1] + 73 + 75 * distance_y / (0 ** distance + distance),
            self.dst_node.pos[0] + 73 - 75 * distance_x / (0 ** distance + distance),
            self.dst_node.pos[1] + 73 - 75 * distance_y / (0 ** distance + distance)
        )

        triangle = self.vector.canvas.before.get_group('triangle')[0]
        triangle.points = (
            line.points[2], line.points[3],
            line.points[2] - 30, line.points[3] - 15,
            line.points[2] - 30, line.points[3] + 15
        )

        rotation = self.vector.canvas.before.get_group('rotation')[0]
        rotation.angle = sign_x * asin(distance_y / (0 ** distance + distance)) * 180 / pi + 180 * 0 ** (1 + sign_x)
        rotation.origin = (triangle.points[0], triangle.points[1])

    def ask_weight(self):
        self.edge_menu.dismiss()
        EdgeAskWeight(self).open()

    def set_weight(self, weight: int):
        self.edge_weight = weight
        self.edge_button.text = str(weight)
        self.parent_tab.graph.set_edge_weight(self.edge_id, weight)

    def remove(self):
        self.edge_menu.dismiss()
        self.parent_tab.remove_edge(self)
