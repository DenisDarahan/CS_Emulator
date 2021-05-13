from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty

from graph import Graph
from interface.popups import ErrorPopup
from .node import Node, AskAddNode
from .edge import Edge, AskAddEdge
from .popups import TaskGraphSave, TaskGraphSaveName, TaskGraphLoadName, AskGenerate


class TaskGraphTab(TabbedPanelItem):
    layout: FloatLayout = ObjectProperty()

    x_scale: int = 2
    y_scale: int = 2

    nodes: list = []
    edges: list = []

    def __init__(self, graph: Graph, **kwargs):
        self.graph = graph
        super().__init__(**kwargs)

    def scale_layout(self):
        self.layout.size[0] += self.layout.size[0] // self.x_scale
        self.x_scale += 1

        incr = self.layout.size[1] // self.y_scale
        self.layout.size[1] += incr
        for child in self.layout.children:
            child.pos[1] += incr

        self.y_scale += 1

    def ask_add_node(self):
        AskAddNode(self).open()

    def add_node(self, node_weight: int) -> Node:
        new_node = Node(len(self.nodes), node_weight, self)

        self.graph.add_node(new_node.node_id, new_node.node_weight, new_node.pos)
        self.layout.add_widget(new_node)
        self.nodes.append(new_node)

        if new_node.pos[0] > self.layout.size[0] // self.x_scale:
            self.scale_layout()

        return new_node

    def remove_node(self, node: Node):
        self.nodes.remove(node)
        while node.edges:
            self.remove_edge(node.edges[0])

        for _node in self.nodes:
            if _node.node_id > node.node_id:
                _node.node_pos = _node.pos
                _node.node_id -= 1
                _node.str_id = str(_node.node_id + 1)
                _node.node_button.text = f'{_node.str_id} | {_node.node_weight}'

        self.graph.remove_node(node.node_id)
        self.layout.remove_widget(node)

    def ask_add_edge(self):
        if len(self.nodes) < 2:
            ErrorPopup('Not enough nodes!\nAdd at least 2 nodes').open()
            return
        AskAddEdge(self).open()

    def add_edge(self, edge_weight: int, src_node: Node, dst_node: Node) -> Edge:
        new_edge = Edge(len(self.edges), edge_weight, self, src_node, dst_node)

        self.graph.add_edge(new_edge.edge_id, new_edge.edge_weight, src_node.node_id, dst_node.node_id)

        if self.graph.has_cycles():
            self.graph.remove_edge(new_edge.edge_id)
            ErrorPopup('Error! Cycle found!').open()

        else:
            self.layout.add_widget(new_edge)
            self.edges.append(new_edge)

            src_node.edges.append(new_edge)
            dst_node.edges.append(new_edge)

        return new_edge

    def remove_edge(self, edge: Edge):
        self.edges.remove(edge)
        edge.src_node.edges.remove(edge)
        edge.dst_node.edges.remove(edge)

        for _edge in self.edges:
            if _edge.edge_id > edge.edge_id:
                _edge.edge_id -= 1

        self.graph.remove_edge(edge.edge_id)
        self.layout.remove_widget(edge)

    def ask_load(self):
        if self.layout.children:
            TaskGraphSave(self, self.ask_load_name).open()
            return
        self.ask_load_name()

    def ask_load_name(self):
        TaskGraphLoadName(self).open()

    def load(self, name: str):
        self.clear_graph()
        self.display_graph(*self.graph.load(name))

    def ask_save_name(self, callback=None):
        if not self.layout.children:
            ErrorPopup('Graph is empty').open()
            return
        TaskGraphSaveName(self, callback).open()

    def save(self, name: str, callback=None):
        self.graph.save(name, self.x_scale, self.y_scale)

        if callback is not None:
            callback()

    def ask_generate(self):
        if self.layout.children:
            TaskGraphSave(self, self.ask_generate_number).open()
            return
        self.ask_generate_number()

    def clear_graph(self):
        self.graph.clear()
        self.nodes.clear()
        self.edges.clear()
        self.layout.clear_widgets()

    def ask_generate_number(self):
        AskGenerate(self).open()

    def generate(self, n_min_weight: int, n_max_weight: int, nodes_number: int, correlation: float,
                 e_min_weight: int, e_max_weight: int):
        self.clear_graph()
        self.display_graph(
            *self.graph.generate(n_min_weight, n_max_weight, nodes_number, correlation, e_min_weight, e_max_weight,
                                 self.layout.size, [self.x_scale, self.y_scale])
        )

    def display_graph(self, graph: Graph, scale_level: [tuple, list]):
        for node in graph.nodes:
            new_node = Node(node.node_id, node.weight, self, node.node_pos)
            self.layout.add_widget(new_node)
            self.nodes.append(new_node)

        for edge in graph.edges:
            src_node = self.nodes[edge.src_node.node_id]
            dst_node = self.nodes[edge.dst_node.node_id]

            new_edge = Edge(edge.edge_id, edge.weight, self, src_node, dst_node)
            self.layout.add_widget(new_edge)
            self.edges.append(new_edge)

            src_node.edges.append(new_edge)
            dst_node.edges.append(new_edge)

        while self.x_scale < scale_level[0] or self.y_scale < scale_level[1]:
            self.scale_layout()
