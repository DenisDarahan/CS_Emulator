from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty

from interface.popups import ErrorPopup


class NodeAskAddEdge(Popup):
    dst_node_id: TextInput = ObjectProperty()
    edge_weight: TextInput = ObjectProperty()

    def __init__(self, parent_tab: TabbedPanelItem, src_node, **kwargs):
        super().__init__(**kwargs)
        self.parent_tab = parent_tab
        self.src_node = src_node

    def add_edge(self):
        self.dismiss()

        try:
            dst_node_id = int(self.dst_node_id.text) - 1
            if (not 0 <= dst_node_id < len(self.parent_tab.nodes)) or \
                    self.src_node.node_id == dst_node_id or \
                    self.parent_tab.graph.adj_matrix[self.src_node.node_id][dst_node_id]:
                raise ValueError(f'Dst Node id must be between 1 and {len(self.parent_tab.nodes)}')

            weight = int(self.edge_weight.text)
            if weight < 1:
                raise ValueError('Weight must be 1 or greater')

        except ValueError as ve:
            ErrorPopup(f'Not correct node id or weight!\n{" ".join(ve.args)}').open()

        else:
            return self.parent_tab.add_edge(weight, self.src_node, self.parent_tab.nodes[dst_node_id])
